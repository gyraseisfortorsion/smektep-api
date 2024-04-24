from .base import Model, ReadModel
import datetime
import uuid
from typing import List, Optional
from dateutil.relativedelta import relativedelta

from pydantic import EmailStr, Field, root_validator, validator, ConfigDict, StringConstraints

class AssignmentCreate(Model):
    subject: str = "Mathematics"
    topic: str = "Algebra"
    grade_level: str = "9th"
    difficulty: int = 1
    quantity: int = 5
    extra_info: Optional[str] = None

class AssignmentUpdate(Model):
    subject: Optional[str]
    topic: Optional[str]
    grade_level: Optional[str]
    difficulty: Optional[int]
    quantity: Optional[int]
    extra_info: Optional[str] = None

