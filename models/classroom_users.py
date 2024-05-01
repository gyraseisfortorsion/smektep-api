from sqlalchemy.orm import relationship
from .base import isActiveModel, Model
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text, Enum
from sqlalchemy.dialects.postgresql import UUID
from core import Base
from datetime import datetime
import uuid


class ClassroomUser(Base):
    __tablename__ = 'classroom_users'
    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    classroom_id = Column(ForeignKey('classrooms.id'), nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    role = Column(Enum('teacher', 'secondary_teacher', 'curator', 'moderator', 'admin', 'assistant', 'student', name='role'), nullable=False)

    classrooms = relationship('Classroom', back_populates='users')
    user = relationship('User', back_populates='classrooms')