from fastapi import FastAPI, HTTPException, Depends, status, Header
from core import settings
from .base import ServiceBase
from models import Post, ClassroomUser
from schemas import PostCreate, PostUpdate, PostRead

from sqlalchemy.orm import Session


class PostService(ServiceBase[Post, PostCreate, PostUpdate]):
    def get_classroom_posts(self, db: Session, classroom_id: str, user_id: str):
        # check is the user is in the classroom
        classroom_user = db.query(ClassroomUser).filter(ClassroomUser.classroom_id == classroom_id, ClassroomUser.user_id == user_id).first()
        if not classroom_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not in this classroom")
        posts = db.query(Post).filter(Post.classroom_id == classroom_id).all()
        return posts
    
    def get_post(self, db: Session, classroom_id: str, post_id: str, user_id: str):
        # check is the user is in the classroom
        classroom_user = db.query(ClassroomUser).filter(ClassroomUser.classroom_id == classroom_id, ClassroomUser.user_id == user_id).first()
        if not classroom_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not in this classroom")
        post = db.query(Post).filter(Post.id == post_id).first()
        return post
    
    def update_post(self, db: Session, post_id: str, user_id: str, body: PostUpdate) -> Post:
        post = self.get_by_id(db, post_id)
        if post.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not the author of this post")
        return super().update(db, db_obj=post, obj_in=body)

    
post_service = PostService(Post)