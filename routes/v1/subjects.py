from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core import get_db, settings
from schemas import SubjectCreate, SubjectRead, SubjectUpdate
from services import auth_service, subject_service

router = APIRouter(prefix="/subjects", tags=["subjects"])

@router.post("")
def create_subject(body: SubjectCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    if auth_service.get_role(credentials.credentials)== "teacher":
        return subject_service.create(db, body)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can create classrooms")
    
@router.get("")
def get_all(db: Session = Depends(get_db)):
    return subject_service.get_all(db)