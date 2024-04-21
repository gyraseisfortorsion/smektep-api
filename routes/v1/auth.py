from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core import get_db
from schemas import LoginForm, UserCreate
from services import auth_service, user_service

router = APIRouter(prefix="/auth", tags=["Authorization"])


@router.post("/login")
async def login(form: LoginForm, db: Session = Depends(get_db)):
    return await auth_service.login_for_access_token(form, db)

# @router.post("/register")
# def register(body: UserCreate, db: Session = Depends(get_db)):
#     if user_service.get_user_by_email(body.email, db):
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
#     user = user_service.create(db, body)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")
#     return "User created successfully"

@router.post("/refresh-token")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    return auth_service.refresh_access_token(refresh_token, db)

@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    return auth_service.logout(refresh_token, db)