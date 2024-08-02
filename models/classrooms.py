from sqlalchemy.orm import relationship
from .base import isActiveModel, Model
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from core import Base
from datetime import datetime
import uuid

class Classroom(Model):
    __tablename__ = 'classrooms'

    name = Column(String)
    subject_id = Column(ForeignKey('subjects.id'))
    school_id = Column(String())

    subject = relationship('Subject', back_populates='classrooms')
    users = relationship('ClassroomUser', back_populates='classroom')
    assignments = relationship('Assignment', back_populates='classroom')
    posts = relationship('Post', back_populates='classroom')