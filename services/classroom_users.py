from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, status, Header
from core import settings
from .base import ServiceBase
from models import ClassroomUser
from schemas import ClassroomUserCreate, ClassroomUserUpdate, UserStudentRead
from datetime import datetime
import uuid
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


class ClassroomUsersService(ServiceBase[ClassroomUser, ClassroomUserCreate, ClassroomUserUpdate]):
    def get_students(self, db: Session, classroom_id: str):
        # print(classroom)
        # print(classroom.students)
        students = db.query(ClassroomUser).filter(ClassroomUser.classroom_id == classroom_id, ClassroomUser.role == 'student').all()
        return [UserStudentRead.from_orm(student.user) for student in students]

classroom_users_service = ClassroomUsersService(ClassroomUser)