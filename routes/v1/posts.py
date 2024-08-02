
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core import get_db, settings
from schemas import PostCreate, PostRead, PostUpdate
from services import auth_service, post_service
from typing import List

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("")
def create_post(body: PostCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    # get user id from token
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    # add author_id to body
    body.author_id = user_id
    if auth_service.get_role(credentials.credentials)== "teacher" or auth_service.get_role(credentials.credentials)== "curator":
        return post_service.create(db, body)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers and curators can create posts")
    
@router.get("/{classroom_id}", response_model=List[PostRead])
def get_all(classroom_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    return post_service.get_classroom_posts(db, classroom_id, user_id)

@router.get("/{classroom_id}/{post_id}", response_model=PostRead)
def get_post(classroom_id: str, post_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    return post_service.get_post(db, classroom_id, post_id, user_id)

@router.put("/{post_id}")
def update_post(post_id: str, body: PostUpdate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    return post_service.update_post(db, post_id, user_id, body)
