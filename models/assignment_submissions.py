from sqlalchemy.orm import relationship
from .base import isActiveModel, Model
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text, Text, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
from core import Base
from datetime import datetime
import uuid

class AssignmentSubmission(Model):
    __tablename__ = 'assignment_submissions'

    student_id = Column(ForeignKey('users.id'), nullable=False)
    assignment_id = Column(ForeignKey('assignments.id', ondelete='CASCADE'), nullable=False)
    submission_date = Column(DateTime(True))
    parent_id = Column(ForeignKey('assignment_submissions.id'))
    grade = Column(Float(53))
    commentaries = Column(Text)
    pdf_url = Column(Text)
    transcription = Column(Text)
    ai_commentary = Column(Text)

    assignment = relationship('Assignment', back_populates='assignment_submissions')
    # parent = relationship('AssignmentSubmission', remote_side='AssignmentSubmission.id', back_populates='children')
    parent = relationship('AssignmentSubmission')
    student = relationship('User', back_populates='assignment_submissions')