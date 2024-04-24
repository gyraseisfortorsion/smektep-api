from .base import isActiveModel, Model, NamedModel
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

class Subject(NamedModel):
    __tablename__ = 'subjects'

    school_id = Column(UUID)

    classrooms = relationship('Classroom', back_populates='subject')

