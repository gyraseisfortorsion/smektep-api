from .base import Model, ReadModel
from datetime import datetime
import uuid
from typing import List, Optional
from dateutil.relativedelta import relativedelta
from .subjects import SubjectRead

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
    name: str
    subject_id: SubjectRead
    school_id: uuid.UUID