from .base import ServiceBase
from fastapi import Depends, HTTPException
from core import get_db
from models import User, UserInfo, StudentInfo, TeacherInfo
from utils import hash_password
from sqlalchemy.orm import Session 
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from schemas import (
    UserCreate,
    UserUpdate,
    UserRead,
    UserInfoCreate,
    UserInfoRead,
    StudentInfoCreateAttach,
    StudentInfoCreate,
    StudentInfoRead,
    TeacherInfoCreate,
    TeacherInfoRead,
    TeacherInfoCreateAttach
)
import uuid
class UserService(ServiceBase[User, UserCreate, UserUpdate]):

    def create(self, db: Session, body: UserCreate):
        # first create user info
        obj_in = jsonable_encoder(body.user_info)
        user_info = UserInfo(**obj_in)
        db.add(user_info)
        db.flush()
        user_info_id = user_info.id
        # then create user
        body.password_hash = hash_password(body.password_hash)
        user = User(**body.dict(exclude={'user_info'}), user_info_id=user_info_id, created_at=datetime.now(), updated_at=datetime.now()) 
        # user.password_hash = hash_password(body.password_hash)
        db.add(user)
        db.commit()
        return user
    
    def create_student_from_user(self, db: Session, body: StudentInfoCreateAttach):
        obj_in = jsonable_encoder(body)
        user = self.get_by_id(db, body.user_id)
        if user.teacher_info is None:
            return HTTPException(status_code=400, detail="TEACHER cannot be assigned as student")
        if user:
            if user.student_info is not None:
                # delete existing student info
                db.delete(user.student_info)
            student_info = StudentInfo(**obj_in)
            db.add(student_info)
            db.commit()
            return student_info
        return None

    def create_teacher_from_user(self, db: Session, body: TeacherInfoCreateAttach):
        obj_in = jsonable_encoder(body)
        user = self.get_by_id(db, body.user_id)
        if user.student_info is None:
            return HTTPException(status_code=400, detail="STUDENT cannot be assigned as teacher")
        if user:
            if user.teacher_info is not None:
                # delete existing teacher info
                db.delete(user.teacher_info)
            teacher_info = TeacherInfo(**obj_in)
            db.add(teacher_info)
            db.commit()
            return teacher_info
        return None
    
    def create_student(self, db: Session, body: StudentInfoCreate):
        user_params = body.user.dict()
        user = self.create(db, UserCreate(**user_params))
        student_info = StudentInfo(**body.dict(exclude={'user'}), user_id=user.id)
        db.add(student_info)
        db.commit()
        return student_info
    
    def create_teacher(self, db: Session, body: TeacherInfoCreate):
        user_params = body.user.dict()
        user = self.create(db, UserCreate(**user_params))
        teacher_info = TeacherInfo(**body.dict(exclude={'user'}), user_id=user.id)
        db.add(teacher_info)
        db.commit()
        return teacher_info

    def get_user_by_email(self, email: str, db: Session):
        return db.query(User).filter(User.email == email).first()
    
    def get_all_users(self, db: Session):
        return db.query(User).all()
    
user_service = UserService(User)
        
        