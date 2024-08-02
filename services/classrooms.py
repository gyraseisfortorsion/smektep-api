from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, status, Header
from core import settings
from .base import ServiceBase
from models import Classroom, ClassroomUser
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
        
    async def get_image(self, db: Session, classroom_id: str):
        classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
        if classroom.background_image:
            return await object_storage_service.s3_download(classroom.background_image)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        
classroom_service = ClassroomService(Classroom)