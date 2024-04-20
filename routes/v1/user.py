from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core import get_db
from schemas import LoginForm, UserCreate, UserRead
from typing import List
from services import user_service, auth_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/me")
def get_me(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(credentials.credentials, db)
    return user

@router.get("", response_model=List[UserRead])
def get_all_users(db: Session = Depends(get_db)):
    return user_service.get_all_users(db)