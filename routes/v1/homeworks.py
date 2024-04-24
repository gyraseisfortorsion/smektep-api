from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core import get_db, settings
from schemas import AssignmentCreate
from services import assignment_service, auth_service

router = APIRouter(prefix="/homeworks", tags=["Homeworks"])

@router.post("/generate/{password}")
async def generate_homework(password: str, body: AssignmentCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):

    if password != settings.PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    elif auth_service.get_role(credentials.credentials)== "teacher":
        hw = await assignment_service.generate_homework(body.subject, body.topic, body.grade_level, body.difficulty, body.quantity)
        return hw
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can generate homework")
