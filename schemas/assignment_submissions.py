from .base import Model, ReadModel
from datetime import datetime
import uuid
from typing import List, Optional
from dateutil.relativedelta import relativedelta
from .user import StudentNameRead
from enum import Enum

from pydantic import EmailStr, Field, root_validator, validator, ConfigDict, StringConstraints

class AssignmentSubmissionCreate(Model):
    student_id: uuid.UUID
    assignment_id: uuid.UUID
    submission_date: datetime
    pdf_url: Optional[str]
    commentaries: Optional[str]

class AssignmentSubmissionMark(ReadModel):
    grade: float

class AssignmentSubmissionResubmit(ReadModel):
    submission_date: datetime
    parent_id: Optional[uuid.UUID]
    commentaries: Optional[str]
    pdf_url: Optional[str]

class AssignmentSubmissionReadShort(Model):
    model_config = ConfigDict(from_attributes=True)

    student_id: uuid.UUID
    submission_date: datetime
    grade: Optional[float]
    commentaries: Optional[str]
    pdf_url: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class AssignmentSubmissionReadTeacher(Model):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    submission_date: datetime
    grade: Optional[float]
    commentaries: Optional[str]
    pdf_url: Optional[str]
    student_info: StudentNameRead
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

