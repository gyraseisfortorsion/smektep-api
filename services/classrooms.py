from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, status, Header
from core import settings
from .base import ServiceBase
from models import Classroom
from schemas import ClassroomCreate, ClassroomUpdate
from datetime import datetime
import uuid
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


class ClassroomService(ServiceBase[Classroom, ClassroomCreate, ClassroomUpdate]):
    pass

classroom_service = ClassroomService(Classroom)