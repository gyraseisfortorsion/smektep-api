from sqlalchemy.orm import relationship
from .base import isActiveModel, Model
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text, Text, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
from core import Base
from datetime import datetime
import uuid

class Post(Model):
    __tablename__ = 'posts'

    classroom_id = Column(ForeignKey('classrooms.id'), nullable=False)
    assignment_id = Column(ForeignKey('assignments.id'))
    title = Column(String(), nullable=False)
    content = Column(Text)
    attachment_link = Column(Text)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime)
    author_id = Column(ForeignKey('users.id'), nullable=False)

    assignment = relationship('Assignment', back_populates='posts')
    classroom = relationship('Classroom', back_populates='posts')
    author = relationship('User', back_populates='posts')
    post_commentaries = relationship('AssignmentPostCommentary', back_populates='post', cascade='all, delete')


"""
create table posts
(
    id              uuid    not null
        constraint posts_pk
            primary key,
    classroom_id    uuid    not null
        constraint posts_classrooms_id_fk
            references classrooms,
    assignment_id   uuid
        constraint posts_assignments_id_fk
            references assignments,
    title           varchar not null,
    description     text,
    attachment_link text,
    created_at      timestamp default now(),
    updated_at      timestamp
);
"""