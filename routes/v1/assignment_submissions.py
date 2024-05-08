from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core import get_db, settings
from schemas import AssignmentSubmissionCreate, AssignmentSubmissionResubmit, AssignmentSubmissionMark, AssignmentSubmissionRead
from services import assignment_service, auth_service, assignment_submission_service

router = APIRouter(prefix="/assignments", tags=["Assignments Submissions"])

@router.post("/upload")
async def upload(assignment_id: str, pdf: UploadFile=File(...), credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    pdf = await pdf.read()
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "student":
        return await assignment_submission_service.upload(pdf, assignment_id, user_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only students can upload assignments")

@router.post("/submit")
def submit(assignment: AssignmentSubmissionCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "student":
        return assignment_submission_service.submit(assignment, user_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only students can submit assignments")
    
@router.get("/submissions/{assignment_id}")
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
        return await assignment_submission_service.check_submission(submission_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can check assignments")
    
@router.get("/{assignment_id}", response_model = AssignmentSubmissionRead, description="Get a submission details by id")
def get_submission(assignment_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "student":
        return assignment_submission_service.get_by_id(db, assignment_id, user_id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only students can view submissions")