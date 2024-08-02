from .base import Model
from datetime import datetime
import uuid
from typing import Optional

from pydantic import ConfigDict



class PostCreate(Model):
    classroom_id: uuid.UUID
    assignment_id: Optional[uuid.UUID]
    title: str
    content: Optional[str]
    attachment_link: Optional[str]

class PostUpdate(Model):
    assignment_id: Optional[uuid.UUID]
    title: str
    content: str
    attachment_link: Optional[str]

class PostRead(Model):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    classroom_id: uuid.UUID
    assignment_id: Optional[uuid.UUID]
    title: str
    content: Optional[str]
    attachment_link: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

