from .base import ServiceBase
from fastapi import Depends
from core import get_db
from models import User
from sqlalchemy.orm import Session 
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
    def get_user_by_email(self, email: str, db: Session):
        return db.query(User).filter(User.email == email).first()
    
user_service = UserService(User)
        
        