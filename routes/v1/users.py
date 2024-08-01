from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core import get_db
from schemas import *
from typing import List
from services import user_service, auth_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserRead)
def get_me(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(credentials.credentials, db)
    print(user.__dict__)
    print(user.user_info.__dict__)
    return user

@router.post("/avatar/upload", description="Upload user avatar")
async def upload_avatar(avatar: UploadFile = File(...), credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(credentials.credentials, db)
    # save image to local directory
    with open(avatar.filename, "wb") as f:
        f.write(avatar.file.read())

    avatar = await user_service.upload_avatar(db, user, avatar.filename)
    if not avatar:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload image")
    return avatar

@router.get("/avatar", description="Download user avatar")
async def get_avatar(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(credentials.credentials, db)
    avatar = await user_service.get_avatar(db, user.id)
    if not avatar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    return Response(
        content=avatar,
        headers={
            'Content-Disposition': f'attachment;filename=avatar.png',
            'Content-Type': 'image/png',
        }
    )

@router.get("/teachers/me", response_model=UserTeacherRead)
def get_teacher_me(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(credentials.credentials, db)
    if user.teacher_info is None:
        raise HTTPException(status_code=400, detail="User is not a teacher")
    return user

@router.get("/students/me", response_model=UserStudentRead)
def get_student_me(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(credentials.credentials, db)
    if user.student_info is None:
        raise HTTPException(status_code=400, detail="User is not a student")
    return user

@router.post("/students/register", response_model=StudentInfoCreate)
def register_student(body: StudentInfoCreate, db: Session = Depends(get_db)):
    return user_service.create_student(db, body)

@router.post("/teachers/register", response_model=TeacherInfoCreate)
def register_teacher(body: TeacherInfoCreate, db: Session = Depends(get_db)):
    return user_service.create_teacher(db, body)

@router.post("/students/attach", response_model=StudentInfoCreateAttach)
def attach_student(body: StudentInfoCreateAttach, db: Session = Depends(get_db)):
    return user_service.create_student_from_user(db, body)

@router.post("/teachers/attach", response_model=TeacherInfoCreateAttach)
def attach_teacher(body: TeacherInfoCreateAttach, db: Session = Depends(get_db)):
    return user_service.create_teacher_from_user(db, body)

@router.get("", response_model=List[UserRead])
def get_all_users(db: Session = Depends(get_db)):
    return user_service.get_all_users(db)