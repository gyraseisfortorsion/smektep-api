from .base import Model, ReadModel
import datetime
import uuid
from typing import List, Optional
from dateutil.relativedelta import relativedelta

from pydantic import EmailStr, Field, root_validator, validator, ConfigDict, StringConstraints

class UserInfoRead(ReadModel):
    first_name: str
    last_name: str
    father_name: Optional[str]
    address: Optional[str]
    gender: bool
    phone_number: Optional[str]

class UserInfoCreate(Model):
    first_name: str
    last_name: str
    father_name: Optional[str]
    address: Optional[str]
    gender: bool
    phone_number: Optional[str]

class UserRead(ReadModel):
    role: int
    email: EmailStr
    last_signed_at: Optional[datetime.datetime]
    user_info: UserInfoRead



class UserCreate(Model):
    model_config = ConfigDict(from_attributes=True)

    role: int
    email: EmailStr
    password_hash: str
    user_info: UserInfoCreate

class UserUpdate(Model):
    model_config = ConfigDict(from_attributes=True)
    
    role: Optional[int]
    email: Optional[EmailStr]
    password: Optional[str]
    user_info: Optional[UserInfoCreate]

class StudentInfoRead(ReadModel):
    # model_config = ConfigDict(from_attributes=True)
    
    grade_level: int
    guardian_phone_number: str
    guardian_first_name: str
    guardian_last_name: str
    guardian_father_name: Optional[str]
    guardian_email: str

class StudentInfoCreateAttach(Model):
    model_config = ConfigDict(from_attributes=True)

    grade_level: int
    guardian_phone_number: str
    guardian_first_name: str
    guardian_last_name: str
    guardian_father_name: Optional[str]
    guardian_email: EmailStr
    user_id: uuid.UUID

class StudentInfoCreate(Model):
    model_config = ConfigDict(from_attributes=True)

    grade_level: int
    guardian_phone_number: str
    guardian_first_name: str
    guardian_last_name: str
    guardian_father_name: Optional[str]
    guardian_email: str
    user: UserCreate

class StudentInfoCreate(Model):
    model_config = ConfigDict(from_attributes=True)
    
    grade_level: int
    guardian_phone_number: str
    guardian_first_name: str
    guardian_last_name: str
    guardian_father_name: Optional[str]
    guardian_email: EmailStr
    user: UserCreate

class UserStudentRead(UserRead):
    # model_config = ConfigDict(from_attributes=True)
    student_info: StudentInfoRead


class TeacherInfoRead(ReadModel):
    model_config = ConfigDict(from_attributes=True)
    
    department_id: uuid.UUID

class TeacherInfoCreate(Model):
    model_config = ConfigDict(from_attributes=True)
    
    department_id: uuid.UUID
    user: UserCreate

class TeacherInfoCreateAttach(Model):
    model_config = ConfigDict(from_attributes=True)
    
    department_id: uuid.UUID
    user_id: uuid.UUID

class UserTeacherRead(UserRead):
    teacher_info: TeacherInfoRead
