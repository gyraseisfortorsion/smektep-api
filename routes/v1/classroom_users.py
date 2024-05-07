from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core import get_db, settings
from schemas import ClassroomUserCreate, ClassroomUserUpdate, UserStudentRead, ClassroomRead, ClassroomStudentRead
from services import auth_service, classroom_users_service
from typing import List

router = APIRouter(prefix="/classroom", tags=["Classrooms"])

@router.post("/assign")
def assign(body: ClassroomUserCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    if auth_service.get_role(credentials.credentials)== "teacher" or auth_service.get_role(credentials.credentials)== "curator":
        return classroom_users_service.create(db, body)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can create classrooms")
    
@router.get("/students/{classroom_id}", response_model=List[UserStudentRead])
def get_classroom_students(classroom_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "teacher":
        return classroom_users_service.get_students(db, classroom_id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can view classrooms")
    
@router.get("/teacher/{teacher_id}", response_model=List[ClassroomRead])
def get_teacher_classrooms(teacher_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    if auth_service.get_role(credentials.credentials)== "teacher":
        return classroom_users_service.get_teacher_classrooms(db, teacher_id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can view classrooms")

@router.get("/student/{student_id}", response_model=List[ClassroomStudentRead])
def get_student_classrooms(student_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    # if auth_service.get_role(credentials.credentials)== "teacher":
    #     return classroom_users_service.get_student_classrooms(db, student_id)
    # else:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can view classrooms")
    return classroom_users_service.get_student_classrooms(db, student_id)