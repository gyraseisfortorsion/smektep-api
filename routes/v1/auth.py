from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer
# from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from core import get_db
from schemas import LoginForm
from services import auth_service

router = APIRouter(prefix="/auth", tags=["Authorization"])


@router.post("/login")
def login(form: LoginForm, db: Session = Depends(get_db)):
    return auth_service.login_for_access_token(form, db)

@router.post("/refresh-token")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    return auth_service.refresh_access_token(refresh_token, db)

@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    return auth_service.logout(refresh_token, db)