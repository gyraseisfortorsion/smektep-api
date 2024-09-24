from sqlalchemy.orm import relationship
from .base import isActiveModel, Model
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text, Text, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
from core import Base
from datetime import datetime
import uuid


class AssignmentPostCommentary(Model):
    __tablename__ = 'assignment_post_commentaries'

    id = Column(UUID, primary_key=True)
    assignment_id = Column(ForeignKey('assignments.id'), nullable=True)
    post_id = Column(ForeignKey('posts.id'), nullable=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    commentary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    assignment = relationship('Assignment', back_populates='assignment_commentaries')
    post = relationship('Post', back_populates='post_commentaries')
    user = relationship('User', back_populates='assignment_post_commentaries')
