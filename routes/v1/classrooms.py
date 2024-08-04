from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core import get_db, settings
from typing import List
from schemas import ClassroomCreate, ClassroomUpdate, ClassroomRead, UserStudentRead, AssignmentRead, ClassroomGradesRead
from services import auth_service, classroom_service

router = APIRouter(prefix="/classrooms", tags=["Classrooms"])

@router.post("")
def create_classroom(body: ClassroomCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    if auth_service.get_role(credentials.credentials)== "teacher":
        return classroom_service.create(db, body)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can create classrooms")

@router.get("/assignments/{classroom_id}", response_model=List[AssignmentRead])
def get_classroom_assignments(classroom_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "teacher":
        return classroom_service.get_assignments(db, classroom_id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can view classrooms")
    
@router.post("/image/upload/{classroom_id}", description="Upload classroom image")
async def upload_image(classroom_id: str, image: UploadFile = File(...), credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    if auth_service.get_role(credentials.credentials)== "teacher":
        # save image to local directory
        with open(image.filename, "wb") as f:
            f.write(image.file.read())
        image = await classroom_service.upload_image(db, user_id, classroom_id, image.filename)
        if not image:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload image")
        return image
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only teachers can upload classroom images")

@router.get("/image/{classroom_id}", description="Download classroom image")
async def get_image(classroom_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    image = await classroom_service.get_image(db, classroom_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return Response(
        content=image,
        headers={
            'Content-Disposition': f'attachment;filename=classroom.png',
            'Content-Type': 'image/png',
        }
    )
    
@router.get("/gradebook/{classroom_id}", response_model=List[ClassroomGradesRead], description="Get all grades for a classroom. ONly for teachers and curators")
def get_classroom_grades(classroom_id: str, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user_id = auth_service.get_current_user(credentials.credentials, db).id
    return classroom_service.get_classroom_grades(db, classroom_id, user_id)


"""
@router.post("/avatar/upload", description="Upload user avatar")
async def upload_avatar(avatar: UploadFile = File(...), credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(credentials.credentials, db)
    # save image to local directory
    with open(avatar.filename, "wb") as f:
        f.write(avatar.file.read())

    avatar = await user_service.upload_avatar(db, user, avatar.filename)
    if not avatar:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload image")
    return avatar

@router.get("/avatar", description="Download user avatar")
async def get_avatar(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(credentials.credentials, db)
    avatar = await user_service.get_avatar(db, user.id)
    if not avatar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    return Response(
        content=avatar,
        headers={
            'Content-Disposition': f'attachment;filename=avatar.png',
            'Content-Type': 'image/png',
        }
    )

"""
    
