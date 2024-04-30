from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core import get_db, settings
from schemas import AssignmentCreate, HomeworkCreate, HomeworkAssignmentCreate
from services import assignment_service, auth_service

router = APIRouter(prefix="/homeworks", tags=["Homeworks"])

@router.post("/generate/{password}")
async def generate_homework(password: str, body: HomeworkAssignmentCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):

    if password != settings.PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    elif auth_service.get_role(credentials.credentials)== "teacher":
        hw = await assignment_service.generate_homework(body.homework.subject, body.homework.topic, body.homework.grade_level, body.homework.difficulty, body.homework.quantity)
        if not hw:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate homework")
        # create assignment in db
        assignment =  await assignment_service.create_homework(db, body.assignment, hw)
        if not assignment:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create assignment")
        return hw
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can generate homework")
