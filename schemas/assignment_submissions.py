from .base import Model, ReadModel
from datetime import datetime
import uuid
from typing import List, Optional
from dateutil.relativedelta import relativedelta

from enum import Enum

from pydantic import EmailStr, Field, root_validator, validator, ConfigDict, StringConstraints

class AssignmentSubmissionCreate(ReadModel):
    student_id: uuid.UUID
    assignment_id: uuid.UUID
    submission_date: datetime
    commentaries: Optional[str]

class AssignmentSubmissionMark(ReadModel):
    grade: float

class AssignmentSubmissionResubmit(ReadModel):
    submission_date: datetime
    parent_id: Optional[uuid.UUID]
    commentaries: Optional[str]
    pdf_url: Optional[str]