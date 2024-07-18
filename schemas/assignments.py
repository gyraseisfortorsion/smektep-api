from .base import Model, ReadModel
from datetime import datetime
import uuid
from typing import List, Optional
from dateutil.relativedelta import relativedelta
from .assignment_submissions import AssignmentSubmissionReadShort
from enum import Enum

from pydantic import EmailStr, Field, root_validator, validator, ConfigDict, StringConstraints

class AssignmentType(str, Enum):
    homework = 'homework'
    quiz = 'quiz'
    exam = 'exam'

class AssignmentRead(Model):
    id: uuid.UUID
    type: AssignmentType
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    classroom_id: uuid.UUID
    description: Optional[str]
    pdf_url: Optional[str]
    max_grade: Optional[float]
    name: str
    problems: Optional[str]
    answers: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
class AssignmentCreate(Model):
    type: AssignmentType
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    classroom_id: uuid.UUID
    description: Optional[str]
    max_grade: Optional[float]
    name: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
class AssignmentUpdate(Model):
    type: AssignmentType
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    classroom_id: uuid.UUID
    description: Optional[str]
    max_grade: Optional[float]
    name: Optional[str]
    problems: Optional[str]
    answers: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class HomeworkCreate(Model):
    subject: str = "Mathematics"
    topic: str = "Algebra"
    grade_level: str = "9th"
    difficulty: int = 1
    quantity: int = 5
    extra_info: Optional[str] = None

class HomeworkAssignmentCreate(AssignmentCreate):
    problems: str
    answers: Optional[str] = None
    user_id: uuid.UUID


class AssignmentsStudentsReadShort(Model):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: AssignmentType
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    classroom_id: uuid.UUID
    description: Optional[str]
    pdf_url: Optional[str]
    max_grade: Optional[float]
    name: str
    problems: Optional[str]
    assignment_submissions: List[AssignmentSubmissionReadShort]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class AssignmentsReadShort(Model):
    model_config = ConfigDict(from_attributes=True)

    type: AssignmentType
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    classroom_id: uuid.UUID
    description: Optional[str]
    pdf_url: Optional[str]
    max_grade: Optional[float]
    name: str
    problems: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class AssignmentSubmissionRead(Model):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    student_id: uuid.UUID
    submission_date: datetime
    grade: Optional[float]
    commentaries: Optional[str]
    pdf_url: Optional[str]
    assignment: AssignmentsReadShort
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


