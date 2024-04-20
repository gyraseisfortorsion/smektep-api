from .base import ServiceBase
from fastapi import Depends
from core import get_db
from models import User, UserInfo
from utils import hash_password
from sqlalchemy.orm import Session 
from fastapi.encoders import jsonable_encoder
from schemas import (
    UserCreate,
    UserUpdate,
    UserRead,
    UserInfoCreate,
    UserInfoRead,
    StudentInfoCreateAttach,
    StudentInfoRead,
    TeacherInfoCreate,
    TeacherInfoRead,
    TeacherInfoCreateAttach
)
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
        user = User(**body.dict(exclude={'user_info'}), user_info_id=user_info_id) 
        # user.password_hash = hash_password(body.password_hash)
        db.add(user)
        db.commit()
        return user


    def get_user_by_email(self, email: str, db: Session):
        return db.query(User).filter(User.email == email).first()
    
    def get_all_users(self, db: Session):
        return db.query(User).all()
    
user_service = UserService(User)
        
        