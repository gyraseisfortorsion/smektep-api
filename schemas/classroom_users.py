from .base import Model, ReadModel
from datetime import datetime
import uuid
from typing import List, Optional
from dateutil.relativedelta import relativedelta
from .subjects import SubjectRead
from .user import UserStudentRead

from enum import Enum

from pydantic import EmailStr, Field, root_validator, validator, ConfigDict, StringConstraints



class ClassroomUserCreate(Model):
    classroom_id: uuid.UUID
    user_id: uuid.UUID
    role: str = "student"

class ClassroomUserUpdate(Model):
    classroom_id: Optional[uuid.UUID]
    user_id: Optional[uuid.UUID]
    role: Optional[str]

class ClassroomUserRead(Model):

    classroom_id: uuid.UUID
    user_id: uuid.UUID
    role: str


