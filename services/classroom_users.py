from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, status, Header
from core import settings
from .base import ServiceBase
from models import ClassroomUser, Classroom
from schemas import ClassroomUserCreate, ClassroomUserUpdate, UserStudentRead, ClassroomRead, ClassroomStudentRead
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

    def get_teacher_classrooms(self, db: Session, teacher_id: str):
        classrooms = db.query(ClassroomUser).filter(ClassroomUser.user_id == teacher_id, ClassroomUser.role == 'teacher').all()
        return [ClassroomRead.from_orm(classroom.classroom) for classroom in classrooms]

    def get_student_classrooms(self, db: Session, student_id: str):
        res = []
        classrooms = db.query(ClassroomUser).filter(ClassroomUser.user_id == student_id, ClassroomUser.role == 'student').all()
        for classroom in classrooms:
            classroom.classroom.teacher = classroom_users_service.get_primary_teacher(db, classroom.classroom_id)
            print(classroom.classroom.teacher.__dict__)
            res.append(ClassroomStudentRead.from_orm(classroom.classroom))
        return res

    def get_primary_teacher(self, db: Session, classroom_id: str):
        teacher = db.query(ClassroomUser).filter(ClassroomUser.classroom_id == classroom_id, ClassroomUser.role == 'teacher').first()
        return teacher.user.user_info
    
classroom_users_service = ClassroomUsersService(ClassroomUser)