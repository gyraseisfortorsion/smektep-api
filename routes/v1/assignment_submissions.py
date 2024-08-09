from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core import get_db, settings
from typing import List
from schemas import AssignmentSubmissionCreate, AssignmentSubmissionResubmit, AssignmentSubmissionMark, AssignmentSubmissionRead, AssignmentSubmissionReadTeacher, ApproveTranscription
from services import assignment_service, auth_service, assignment_submission_service

router = APIRouter(prefix="/assignments", tags=["Assignments Submissions"])

@router.post("/upload")
async def upload(assignment_id: str, pdf: UploadFile=File(...), credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    filename = pdf.filename
    pdf = await pdf.read()
    # get the filename of the pdf
    
    file_ext = filename.split(".")[-1]
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "student":
        return await assignment_submission_service.upload(pdf, assignment_id, user_id, file_ext, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only students can upload assignments")

@router.post("/submit")
def submit(assignment: AssignmentSubmissionCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "student":
        return assignment_submission_service.submit(assignment, user_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only students can submit assignments")

@router.get("/download/{submission_id}")
async def download(submission_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    pdf = await assignment_submission_service.download(submission_id, user_id, db)
    if pdf:
        return Response(
            content=pdf,
            headers={
                'Content-Disposition': f'attachment;filename={submission_id}.pdf',
                'Content-Type': 'application/octet-stream',
            }
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
@router.get("/submissions/by_assignment/{assignment_id}", response_model = List[AssignmentSubmissionReadTeacher], description="Get all submissions for an assignment")
def get_submissions(assignment_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "teacher":
        return assignment_submission_service.get_submissions(assignment_id, user_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can view submissions")
    
@router.get("/check/{submission_id}")
async def check(submission_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    # user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "teacher":
        return await assignment_submission_service.check_submission_gpt(submission_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can check assignments")

@router.get("/transcribe/{submission_id}")
async def transcribe(submission_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    # user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "teacher" or auth_service.get_role(credentials.credentials)== "student":
        return await assignment_submission_service.transcribe_gpt(submission_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers and students can transcribe assignment submissions")

@router.post("/transcribe/approve")
def approve_transcription(body: ApproveTranscription, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    # user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "student":
        return assignment_submission_service.save_transcription(body.submission_id, body.transcription, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only students can approve transcriptions")
    
@router.get("/submissions/transcription/{submission_id}")
def get_transcription(submission_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    # user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "teacher" or auth_service.get_role(credentials.credentials)== "student":
        return assignment_submission_service.get_transcription(submission_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers and students can view transcriptions")

@router.get("/check/transcription/{submission_id}")
async def check_transcription(submission_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    # user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "teacher":
        return await assignment_submission_service.check_submission_from_transcription(submission_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can check assignment submissions")
    
@router.get("/submissions/{submission_id}", response_model = AssignmentSubmissionRead, description="Get a submission details by submission id")
def get_submission(submission_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "student" or auth_service.get_role(credentials.credentials)== "teacher":
        return assignment_submission_service.get_submission_by_id(db, submission_id, user_id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only submission owner or the teacher can view the submission")

@router.get("/{assignment_id}", response_model = AssignmentSubmissionRead, description="Get a submission details by assignment id")
def get_submission(assignment_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "student":
        return assignment_submission_service.get_by_id(db, assignment_id, user_id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only students can view submissions")
    
@router.patch("/mark")
def mark(body: AssignmentSubmissionMark, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "teacher":
        return assignment_submission_service.mark(body, user_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can mark assignments")