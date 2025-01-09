import requests
import json

from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, status, Header, UploadFile, File
# from core import settings
# from .base import ServiceBase
from models import Assignment, ClassroomUser, Classroom, User
from schemas import AssignmentCreate, AssignmentUpdate, HomeworkAssignmentCreate, AssignmentsStudentsReadShort
from datetime import datetime
# from .object_storage import object_storage_service
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# import uuid
# from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
# import markdown2
# import pdfkit
# from jinja2 import Environment, FileSystemLoader
# from abc import ABC, abstractmethod

def create_test_students(number_of_students):
    url = "http://localhost:8001/api/v1/users/students/register"
    headers = {
        'Content-Type': 'application/json'
    }
    for i in range(number_of_students):

        data = {
            "grade_level": 5,
            "guardian_phone_number": "777777777",
            "guardian_first_name": "string",
            "guardian_last_name": "string",
            "guardian_father_name": "string",
            "guardian_email": f"test_student_guardian_nov{i}@example.com",
            "user": {
                "role": "student",
                "email": f"test_student_nov{i}@example.com",
                "password_hash": "123456",
                "user_info": {
                    "first_name": f"Student{i}",
                    "last_name": f"lastname{i}",
                    "father_name": "string",
                    "address": "string",
                    "gender": True,  # Assuming True represents male, False would represent female
                    "phone_number": "string"
                }
            }
        }
        response = requests.request(
            "POST", url, headers=headers, data=json.dumps(data))
        print(response.text)
        print(response.status_code)
    return "Students created successfully"


def create_test_teachers(number_of_teachers):
    url = "http://localhost:8001/api/v1/users/teachers/register"
    headers = {
        'Content-Type': 'application/json'
    }
    for i in range(number_of_teachers):

        data = {
            "department_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "user": {
                "role": "teacher",
                "email": f"test_teacher_nov{i}@example.com",
                "password_hash": "123456",
                "user_info": {
                    "first_name": f"Teacher{i}",
                    "last_name": f"lastname{i}",
                    "father_name": "string",
                    "address": "string",
                    "gender": True,  # Assuming True represents male, False would represent female
                    "phone_number": "77777777777"
                }
            }
        }
        response = requests.request(
            "POST", url, headers=headers, data=json.dumps(data))
        print(response.text)
        print(response.status_code)
    return "Teachers created successfully"

def create_test_classrooms_and_add_users(number_of_classrooms, db: Session):
    for i in range(number_of_classrooms):
        classroom = Classroom(
            name=f"Classroom_nov{i}",
            grade_level=5,
            subject_id="663365b2-8b48-4e21-800c-dadf52586986",
            school_id="3fa85f64-5717-4562-b3fc-2c963f66afa6"
        )
        db.add(classroom)
        db.flush()
        test_teacher = db.query(User).filter(User.email == f"test_teacher_nov{i}@example.com").first()
        test_student = db.query(User).filter(User.email == f"test_studen_nov{i}@example.com").first()
        classroom_user_teacher = ClassroomUser(
            classroom_id=classroom.id,
            user_id=test_teacher.id,
            role="teacher"
        )
        classroom_user_student = ClassroomUser(
            classroom_id=classroom.id,
            user_id=test_student.id,
            role="student"
        )
        db.add(classroom_user_teacher)
        db.add(classroom_user_student)
    db.commit()
create_test_students(10)
create_test_teachers(2)