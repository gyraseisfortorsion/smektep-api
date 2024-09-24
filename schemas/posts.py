from .base import Model
from datetime import datetime
import uuid
from typing import Optional
from .user import UserPostInfo

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
    author: UserPostInfo
    created_at: datetime
    updated_at: Optional[datetime]

class PostCommentaryRead(Model):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    post_id: uuid.UUID
    user_id: uuid.UUID
    commentary: str
    created_at: datetime
    updated_at: Optional[datetime]

class PostCommentaryCreate(Model):
    post_id: uuid.UUID
    commentary: str

