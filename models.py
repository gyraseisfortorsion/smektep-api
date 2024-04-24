# coding: utf-8
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(UUID, primary_key=True)
    name = Column(String)
    name_ru = Column(String)
    name_kz = Column(String)
    school_id = Column(UUID)


class UserInfo(Base):
    __tablename__ = 'user_info'

    id = Column(UUID, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    father_name = Column(String)
    address = Column(String)
    gender = Column(Boolean)
    phone_number = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Classroom(Base):
    __tablename__ = 'classrooms'

    id = Column(UUID, primary_key=True)
    name = Column(String)
    subject_id = Column(ForeignKey('subjects.id'))
    school_id = Column(UUID)
    created_at = Column(DateTime, server_default=text("now()"))
    updated_at = Column(DateTime, server_default=text("now()"))

    subject = relationship('Subject')


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True)
    user_info_id = Column(ForeignKey('user_info.id', ondelete='SET NULL'), nullable=False)
    is_active = Column(Boolean, nullable=False)
    school_id = Column(UUID)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    password_hash = Column(String, nullable=False)
    email = Column(String, nullable=False)
    last_signed_at = Column(DateTime)
    role = Column(Enum('teacher', 'secondary_teacher', 'curator', 'moderator', 'admin', 'assistant', 'student', name='role'))

    user_info = relationship('UserInfo')


class Assignment(Base):
    __tablename__ = 'assignments'

    id = Column(UUID, primary_key=True)
    type = Column(Enum('homework', 'quiz', 'exam', name='assignment_type'), nullable=False)
    date_from = Column(DateTime(True))
    date_to = Column(DateTime(True))
    classroom_id = Column(ForeignKey('classrooms.id'), nullable=False)
    description = Column(Text)
    pdf_url = Column(Text)
    max_grade = Column(Float(53))
    name = Column(String, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    classroom = relationship('Classroom')


class ClassroomUser(Base):
    __tablename__ = 'classroom_users'

    id = Column(UUID, primary_key=True)
    classroom_id = Column(ForeignKey('classrooms.id'), nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    role = Column(Enum('teacher', 'secondary_teacher', 'curator', 'moderator', 'admin', 'assistant', 'student', name='role'), nullable=False)

    classroom = relationship('Classroom')
    user = relationship('User')


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(UUID, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    user = relationship('User')


class StudentInfo(Base):
    __tablename__ = 'student_info'

    id = Column(UUID, primary_key=True)
    grade_level = Column(Integer)
    guardian_phone_number = Column(String)
    guardian_first_name = Column(String)
    guardian_last_name = Column(String)
    guardian_father_name = Column(String)
    guardian_email = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    user = relationship('User')


class TeacherInfo(Base):
    __tablename__ = 'teacher_info'

    id = Column(UUID, primary_key=True)
    department_id = Column(UUID)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship('User')


class AssignmentSubmission(Base):
    __tablename__ = 'assignment_submissions'

    id = Column(UUID, primary_key=True)
    student_id = Column(ForeignKey('users.id'), nullable=False)
    assignment_id = Column(ForeignKey('assignments.id'), nullable=False)
    submission_date = Column(DateTime(True))
    parent_id = Column(ForeignKey('assignment_submissions.id'))
    grade = Column(Float(53))
    commentaries = Column(Text)
    pdf_url = Column(Text)

    assignment = relationship('Assignment')
    parent = relationship('AssignmentSubmission', remote_side=[id])
    student = relationship('User')
