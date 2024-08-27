from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core import get_db, settings
from schemas import AssignmentCreate, HomeworkCreate, HomeworkAssignmentCreate, MultipleChoiceCreate, WordProblemCreate
from services import assignment_service, auth_service
import os
router = APIRouter(prefix="/assignments", tags=["Assignments"])

@router.post("/word-problems/generate")
async def generate_word_problems(body: WordProblemCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials) == "teacher":
        if body.language:
            word_problems = await assignment_service.generate_word_problems(
                subject_aim=body.subject_aim,
                topic=body.topic,
                num_questions=body.num_questions,
                thematic=body.thematic,
                language=body.language
            )
        else:
            word_problems = await assignment_service.generate_word_problems(
                subject_aim=body.subject_aim,
                topic=body.topic,
                num_questions=body.num_questions,
                thematic=body.thematic
            )
        if not word_problems:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate word problems")
        return word_problems
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can generate word problems")


@router.post("/multiple-choice/generate")
async def generate_multiple_choice_questions(body: MultipleChoiceCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials) == "teacher":
        if body.language:
            mcq = await assignment_service.generate_multiple_choice_questions(
                subject=body.subject,
                topic=body.topic,
                grade_level=body.grade_level,
                difficulty=body.difficulty,
                num_questions=body.num_questions,
                num_choices=body.num_choices,
                extra_info=body.extra_info,
                language=body.language
            )
        else:
            mcq = await assignment_service.generate_multiple_choice_questions(
                subject=body.subject,
                topic=body.topic,
                grade_level=body.grade_level,
                difficulty=body.difficulty,
                num_questions=body.num_questions,
                num_choices=body.num_choices,
                extra_info=body.extra_info
            )
        if not mcq:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate multiple choice questions")
        return mcq
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can generate multiple choice questions")
    
@router.post("/homework/generate/{password}")
async def generate_homework(password: str, body: HomeworkCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if password != settings.PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    elif auth_service.get_role(credentials.credentials)== "teacher":
        if body.language:
            hw = await assignment_service.generate_homework(body.subject, body.topic, body.grade_level, body.difficulty, body.quantity, user_id, body.extra_info, body.language)
        else:
            hw = await assignment_service.generate_homework(body.subject, body.topic, body.grade_level, body.difficulty, body.quantity, user_id, body.extra_info)
        if not hw:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate homework")
        return hw
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can generate homework")

@router.post("/homework/approve")
async def approve_homework(homework: HomeworkAssignmentCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "teacher" and homework.user_id==user_id:
        hw = await assignment_service.approve_homework(homework, db)
        if not hw:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="You do not have access to approve this homework")
        return hw
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can approve homework")
    
@router.post("/homework/create", description="Create a homework assignment from existing pdf")
async def create_from_pdf(body: AssignmentCreate, filename: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    if auth_service.get_role(credentials.credentials)== "teacher":
        hw = await assignment_service.create_from_pdf(body, filename, db)
        if not hw:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create homework")
        return hw
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can create homework")
    
@router.post("/homework/upload", description="Upload a homework assignment")
async def upload_homework(pdf: UploadFile = File(...), credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    # save pdf to local directory first
    with open(pdf.filename, "wb") as f:
        f.write(pdf.file.read())
    if auth_service.get_role(credentials.credentials)== "teacher":
        hw = await assignment_service.upload_pdf_to_s3(pdf.filename)
        # remove file
        os.remove(pdf.filename)
        if not hw:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload homework")
        return hw
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can upload homework")

@router.get("/homework/download/{assignment_id}", description="Download a homework assignment")
async def download_homework(assignment_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    hw = await assignment_service.download_pdf_from_s3(assignment_id, user_id, db)
    if not hw:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to download homework")
    return Response(
            content=hw,
            headers={
                'Content-Disposition': f'attachment;filename={assignment_id}.pdf',
                'Content-Type': 'application/octet-stream',
            }
        )
    
@router.get("/teacher/{classroom_id}", description="Get all assignments for a classroom FOR TEACHER")
def get_all_teacher_assignments(classroom_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "teacher":
        return assignment_service.get_all_teacher_assignments(classroom_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can view homework")

@router.get("/student/{classroom_id}", description="Get all assignments for a classroom FOR STUDENT")
def get_all_student_assignments(classroom_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "student":
        return assignment_service.get_all_student_assignments(classroom_id, user_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only students can view homework")

@router.get("/student/{classroom_id}/{assignment_id}", description="Get assignment for a classroom FOR STUDENT")
def get_student_assignment(classroom_id: str, assignment_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "student":
        return assignment_service.get_student_assignment(classroom_id, assignment_id, user_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only students can view homework")
    
@router.get("/teacher/{classroom_id}/{assignment_id}", description="Get assignment for a classroom FOR TEACHER")
def get_teacher_assignment(classroom_id: str, assignment_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "teacher":
        return assignment_service.get_teacher_assignment(classroom_id, assignment_id, user_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can view homework")
    
@router.get("/delete/{assignment_id}", description="Get all students for an assignment FOR TEACHER")
def delete_assignment(assignment_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "teacher":
        return assignment_service.delete(assignment_id, user_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can delete homework")
    
