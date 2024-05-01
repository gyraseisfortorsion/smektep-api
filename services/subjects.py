from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, status, Header
from core import settings
from .base import ServiceBase
from models import Subject
from schemas import SubjectCreate, SubjectUpdate
from datetime import datetime
import uuid
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


class SubjectService(ServiceBase[Subject, SubjectCreate, SubjectUpdate]):
    def get_all(self, db: Session):
        return db.query(Subject).all()

subject_service = SubjectService(Subject)