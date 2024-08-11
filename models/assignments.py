from sqlalchemy.orm import relationship
from .base import isActiveModel, Model
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text, Text, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
from core import Base
from datetime import datetime
import uuid


class Assignment(Model):
    __tablename__ = 'assignments'

    id = Column(UUID, primary_key=True)
    type = Column(Enum('homework', 'quiz', 'exam', name='assignment_type'), nullable=False)
    date_from = Column(DateTime(True))
    date_to = Column(DateTime(True))
    classroom_id = Column(ForeignKey('classrooms.id'), nullable=False)
    description = Column(Text)
    pdf_url = Column(Text)
    max_grade = Column(Float(53))
    title = Column(String, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    answers = Column(Text)
    problems = Column(Text)

    classroom = relationship('Classroom', back_populates='assignments')
    assignment_submissions = relationship('AssignmentSubmission', back_populates='assignment', cascade='all, delete')
    posts = relationship('Post', back_populates='assignment', cascade='all, delete')