from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core import get_db, settings
from typing import List
from schemas import ClassroomCreate, ClassroomUpdate, ClassroomRead, UserStudentRead
from services import auth_service, classroom_service

router = APIRouter(prefix="/classrooms", tags=["Classrooms"])

@router.post("")
def create_classroom(body: ClassroomCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    if auth_service.get_role(credentials.credentials)== "teacher":
        return classroom_service.create(db, body)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can create classrooms")
    
