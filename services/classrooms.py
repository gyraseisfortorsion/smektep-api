from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, status, Header
from core import settings
from .base import ServiceBase
from models import Classroom, ClassroomUser, User
from schemas import ClassroomCreate, ClassroomUpdate
from datetime import datetime
import uuid
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from .object_storage import object_storage_service
import os


class ClassroomService(ServiceBase[Classroom, ClassroomCreate, ClassroomUpdate]):
    def get_assignments(self, db: Session, classroom_id: str):
        classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
        return classroom.assignments

    async def upload_image(self, db: Session, user_id, classroom_id: str, filename: str):
        classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
        classroom_user = db.query(ClassroomUser).filter(ClassroomUser.classroom_id == classroom_id, ClassroomUser.user_id == user_id).first()
        if not classroom_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have access to upload image for this classroom")
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                avatar = file.read()
                # get the file type
                ext = filename.split('.')[-1]
                s3_filename = "classroom_images/" + str(classroom_id) + '.' + ext
                await object_storage_service.s3_upload(avatar, s3_filename)
                classroom.background_image = s3_filename
                db.commit()
                return classroom
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload image")
    
    def join_classroom(self, db: Session, user_id: str, classroom_code: str):
        # create classroom_user
        classroom = db.query(Classroom).filter(Classroom.id == classroom_code).first()
        user = db.query(User).filter(User.id == user_id).first()
        if not classroom:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")
        classroom_user = db.query(ClassroomUser).filter(ClassroomUser.classroom_id == classroom_code, ClassroomUser.user_id == user_id).first()
        if classroom_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are already in this classroom")
        classroom_user = ClassroomUser(classroom_id=classroom_code, user_id=user_id, role=user.role)
        db.add(classroom_user)
        db.commit()
        return classroom_user
    async def get_image(self, db: Session, classroom_id: str):
        classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
        if classroom.background_image:
            return await object_storage_service.s3_download(classroom.background_image), classroom.background_image
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        
    def get_classroom_grades_for_teacher(self, db: Session, classroom_id: str, user_id: str):
        classroom_user = db.query(ClassroomUser).filter(ClassroomUser.classroom_id == classroom_id, ClassroomUser.user_id == user_id).first()
        if not classroom_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not in this classroom")
        if classroom_user.role not in ["teacher", "secondary_teacher", "curator"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can view grades")
        
        classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
        grades = []
        for assignment in classroom.assignments:
            for submission in assignment.assignment_submissions:
                # Assuming there's a Student model with a method to get the full name by student_id
                student = submission.student
                student_info = student.user_info  # Assuming the Student model has a full_name attribute
                grade_info = {
                    "assignment_id": assignment.id,
                    "assignment_name": assignment.title,
                    "date_to": assignment.date_to,
                    "grade": submission.grade,
                    "student_info": student_info,
                    "student_id": submission.student_id,
                    "max_grade": assignment.max_grade
                }
                grades.append(grade_info)
        grades = sorted(grades, key=lambda x: x['date_to'])
        return grades
    
    def get_classroom_grades_for_student(self, db: Session, classroom_id: str, user_id: str):
        classroom_user = db.query(ClassroomUser).filter(ClassroomUser.classroom_id == classroom_id, ClassroomUser.user_id == user_id).first()
        if not classroom_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not in this classroom")
        if classroom_user.role != "student":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only students can view grades")
        
        classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
        grades = []
        for assignment in classroom.assignments:
            for submission in assignment.assignment_submissions:
                if submission.student_id == user_id:
                    student = submission.student
                    student_info = student.user_info
                    grade_info = {
                        "assignment_id": assignment.id,
                        "assignment_name": assignment.title,
                        "date_to": assignment.date_to,
                        "grade": submission.grade,
                        "student_info": student_info,
                        "student_id": submission.student_id,
                        "max_grade": assignment.max_grade
                    }
                    grades.append(grade_info)
        grades = sorted(grades, key=lambda x: x['date_to'])
        return grades
    
    def get_all_grades_for_teacher(self, db: Session, user_id: str):
        user = db.query(User).filter(User.id == user_id).first()
        classrooms = user.classrooms
        if user.role not in ["teacher", "secondary_teacher", "curator"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can view grades")
        res = []
        grades_by_classroom = {}
        for classroom in classrooms:
            grades = []
            for assignment in classroom.classroom.assignments:
                for submission in assignment.assignment_submissions:
                    # Assuming there's a Student model with a method to get the full name by student_id
                    student = submission.student
                    student_info = student.user_info
                    grade_info = {  
                        "assignment_id": assignment.id,
                        "assignment_name": assignment.title,
                        "date_to": assignment.date_to,
                        "grade": submission.grade,
                        "student_info": student_info,
                        "student_id": submission.student_id,
                        "max_grade": assignment.max_grade
                    }
                    grades.append(grade_info)
                grades = sorted(grades, key=lambda x: x['date_to'])
            grades_by_classroom["classroom_id"] = classroom.classroom.id
            grades_by_classroom["classroom_name"] = classroom.classroom.name
            grades_by_classroom["gradebook"] = grades
            res.append(grades_by_classroom)
            grades_by_classroom={}
        return res
    
    def get_all_grades_for_student(self, db: Session, user_id: str):
        user = db.query(User).filter(User.id == user_id).first()
        classrooms = user.classrooms
        if user.role != "student":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only students can view grades")
        res = []
        grades_by_classroom = {}
        for classroom in classrooms:
            grades = []
            for assignment in classroom.classroom.assignments:
                for submission in assignment.assignment_submissions:
                    if submission.student_id == user_id:
                        student = submission.student
                        student_info = student.user_info
                        grade_info = {
                            "assignment_id": assignment.id,
                            "assignment_name": assignment.title,
                            "date_to": assignment.date_to,
                            "grade": submission.grade,
                            "student_info": student_info,
                            "student_id": submission.student_id,
                            "max_grade": assignment.max_grade
                        }
                        grades.append(grade_info)
                grades = sorted(grades, key=lambda x: x['date_to'])
            grades_by_classroom["classroom_id"] = classroom.classroom.id
            grades_by_classroom["classroom_name"] = classroom.classroom.name
            grades_by_classroom["gradebook"] = grades
            res.append(grades_by_classroom)
            grades_by_classroom={}
        return res
    # def generate_code(self, db: Session, classroom_id):

        
classroom_service = ClassroomService(Classroom)