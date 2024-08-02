from .base import Model, ReadModel
from datetime import datetime
import uuid
from typing import List, Optional
from dateutil.relativedelta import relativedelta
from .subjects import SubjectRead
from .user import UserInfoFullName
from enum import Enum

from pydantic import EmailStr, Field, root_validator, validator, ConfigDict, StringConstraints



class ClassroomCreate(Model):
    name: str
    subject_id: uuid.UUID
    school_id: uuid.UUID

class ClassroomUpdate(Model):
    name: str
    subject_id: uuid.UUID
    school_id: uuid.UUID

class ClassroomRead(Model):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    subject: SubjectRead
    school_id: uuid.UUID
    background_image: Optional[str]

class ClassroomStudentRead(Model):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    teacher: UserInfoFullName
    subject: SubjectRead
    school_id: uuid.UUID