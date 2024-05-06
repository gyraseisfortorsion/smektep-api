from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core import get_db, settings
from schemas import AssignmentSubmissionCreate, AssignmentSubmissionResubmit, AssignmentSubmissionMark
from services import assignment_service, auth_service

router = APIRouter(prefix="/assignments", tags=["Assignments Submissions"])

@router.post("/submit")
def submit(body: AssignmentSubmissionCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "student":
        return assignment_service.submit(body, user_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only students can submit assignments")