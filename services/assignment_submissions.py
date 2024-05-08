from fastapi import FastAPI, HTTPException, Depends, status, Header, UploadFile, File
from core import settings
from .base import ServiceBase
from models import ClassroomUser, Classroom, Assignment, AssignmentSubmission
from schemas import AssignmentSubmissionCreate, AssignmentSubmissionResubmit, AssignmentSubmissionMark
from datetime import datetime
import uuid
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from .classroom_users import classroom_users_service
from .object_storage import object_storage_service
from openai import OpenAI
import google.generativeai as genai
import google.ai.generativelanguage as glm
import pathlib
from pdf2image import convert_from_path
import numpy as np
import PIL
from PIL import Image
import pytz
import shutil
import os

class AssignmentSubmissionService(ServiceBase[AssignmentSubmission, AssignmentSubmissionCreate, AssignmentSubmissionResubmit]):

    def submit(self, body: AssignmentSubmissionCreate, user_id: str, db: Session):
        assignment = db.query(Assignment).filter(Assignment.id == body.assignment_id).first()

        student_classrooms = classroom_users_service.get_student_classrooms(db, user_id)

        if assignment.classroom_id not in [classroom.id for classroom in student_classrooms]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignment is not in any of the student's classrooms")

        if assignment:

            # # UPLOAD PDF TO S3
            # filename_in_s3 = f"{assignment.id}/{pdf.filename}"
            # await object_storage_service.s3_upload(pdf, filename_in_s3)

            # if assignment.date_to.replace(tzinfo=pytz.UTC) < datetime.now(pytz.UTC):
            #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignment is past due date")
            submission = AssignmentSubmission(
                id = str(uuid.uuid4()),
                student_id = user_id,
                assignment_id=body.assignment_id,
                submission_date=datetime.now(),
                pdf_url=body.pdf_url,
            )
            db.add(submission)
            db.commit()
            db.refresh(submission)
            return submission
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    def resubmit(self, body: AssignmentSubmissionResubmit, user_id: str, db: Session):
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == body.submission_id).first()
        if submission:
            if submission.assignment.due_date < datetime.now():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignment is past due date")
            submission.submission = body.submission
            submission.submitted_at = datetime.now()
            db.commit()
            db.refresh(submission)
            return submission
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    def mark(self, body: AssignmentSubmissionMark, db: Session):
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == body.submission_id).first()
        if submission:
            submission.marks = body.marks
            db.commit()
            db.refresh(submission)
            return submission
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    
    async def get_assignment_from_submission(self, submission: AssignmentSubmission, db: Session):
        pdf = await object_storage_service.s3_download(submission.assignment.pdf_url)
        if not os.path.exists('services/temp/homeworks'):
            os.makedirs('services/temp/homeworks')
        path = f"services/temp/{submission.assignment.pdf_url}"
        with open(path, "wb") as f:
            f.write(pdf)
        return path
        
    def get_submissions(self, assignment_id: str, user_id: str, db: Session):
        # check is the teacher is allowed to see this assignment submissions
        teacher_classrooms = classroom_users_service.get_teacher_classrooms(db, user_id)
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if assignment.classroom_id not in [classroom.id for classroom in teacher_classrooms]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Teacher is not in the classroom of the assignment")
        else:
            submissions = db.query(AssignmentSubmission).filter(AssignmentSubmission.assignment_id == assignment_id).all()
            return submissions
    
    async def upload(self, pdf: bytes, assignment_id: str, user_id: str, db: Session):
        filename_in_s3 = f"{assignment_id}/{user_id}.pdf"
        await object_storage_service.s3_upload(pdf, filename_in_s3)
        return filename_in_s3
    
    async def check_submission(self, submission_id: str, db: Session):
        # client = OpenAI(api_key=settings.OPENAI_API_KEY)
        if not os.path.exists('services/temp'):
            os.makedirs('services/temp')

        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro-vision')
        # get pds submission from s3
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
        print(submission.pdf_url)
        pdf = await object_storage_service.s3_download(submission.pdf_url)
        # save pdf locally
        with open(f"services/temp/{submission.pdf_url}", "wb") as f:
            f.write(pdf)
            
        print(f"services/temp/{submission.pdf_url}")
        # images = convert_from_path(f"services/temp/{submission.pdf_url}")
        images = convert_from_path(f'services/temp/{submission.pdf_url}')
        image_paths = []
        for i in range(len(images)):
            if not os.path.exists('services/temp/images/submission'):
                os.makedirs('services/temp/images/submission')
            # Save pages as images in the pdf
            image_path = 'services/temp/images/submission/'+ str(i) +'.jpg'
            image_paths.append(image_path)
            images[i].save(image_path, 'JPEG')
        imgs    = [Image.open(i) for i in image_paths]
        # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
        min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
        imgs_comb = np.vstack([i.resize(min_shape) for i in imgs])
        imgs_comb = Image.fromarray( imgs_comb)
        imgs_comb.save( 'vertical_submission.jpg' )
        

        # now do same but for the assignment pdf itself
        assignment_pdf_path = await self.get_assignment_from_submission(submission, db)
        images2 = convert_from_path(f'{assignment_pdf_path}')
        image_paths2 = []
        for i in range(len(images)):
            # create temp directory for images
            if not os.path.exists('services/temp/images/assignment'):
                os.makedirs('services/temp/images/assignment')
            # Save pages as images in the pdf
            image_path = 'services/temp/images/assignment/'+ str(i) +'.jpg'
            image_paths2.append(image_path)
            images2[i].save(image_path, 'JPEG')
        imgs    = [Image.open(i) for i in image_paths]
        # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
        min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
        imgs_comb = np.vstack([i.resize(min_shape) for i in imgs])
        imgs_comb = Image.fromarray( imgs_comb)
        imgs_comb.save( 'vertical_assignment.jpg' )

        # cleanup temp directories after jpgs are generated
        shutil.rmtree('services/temp')

        # assignment_image = Image.open('vertical_assignment.jpg')
        # submission_image = Image.open('vertical_submission.jpg')
        # send to gemini
        # response = model.generate_content(["Write a short, engaging blog post based on this picture. It should include a description of the meal in the photo and talk about my journey meal prepping.", img], stream=True)
        # response.resolve()

        response = model.generate_content(
            glm.Content(
                parts = [
                    glm.Part(text="Check the submitted work based on the provided answers, and provide detailed feedback and final mark"),
                    glm.Part(
                        inline_data=glm.Blob(
                            mime_type='image/jpeg',
                            data=pathlib.Path('vertical_assignment.jpg').read_bytes()
                        )
                    ),
                    glm.Part(
                        inline_data=glm.Blob(
                            mime_type='image/jpeg',
                            data=pathlib.Path('vertical_submission.jpg').read_bytes()
                        )
                    ),
                ],
            ),
            stream=True)
        response.resolve()
        print(response.text)
        return response.text
    

        
assignment_submission_service = AssignmentSubmissionService(AssignmentSubmission)
