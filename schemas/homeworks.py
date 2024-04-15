from .base import Model, ReadModel
import datetime
import uuid
from typing import List, Optional
from dateutil.relativedelta import relativedelta

from pydantic import EmailStr, Field, root_validator, validator, ConfigDict, StringConstraints

class HomeworkCreate(Model):
    subject: str = "Mathematics"
    topic: str = "Algebra"
    grade_level: str = "9th"
    difficulty: int = 1
    quantity: int = 5