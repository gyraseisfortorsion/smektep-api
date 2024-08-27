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
from models import ClassroomUser
import openai
import base64
from langchain_community.chat_models import ChatOpenAI
from langchain.schema.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pylatexenc.latex2text import LatexNodes2Text

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
            temp_file_urls = f'["{body.file_urls}"]'
            submission = AssignmentSubmission(
                id = str(uuid.uuid4()),
                student_id = user_id,
                assignment_id=body.assignment_id,
                submission_date=datetime.now(),
                file_urls=temp_file_urls,
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

    def mark(self, body: AssignmentSubmissionMark, user_id: str, db: Session):
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == body.id).first()
        assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
        classroom_user = db.query(ClassroomUser).filter(ClassroomUser.user_id == user_id, ClassroomUser.classroom_id == assignment.classroom_id).first()
        if not classroom_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Teacher is not in the classroom of the assignment")
        if not classroom_user.role == "teacher":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only teachers can mark assignments")
        if body.grade > assignment.max_grade:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Grade is higher than the max grade for the assignment")
        if submission:
            submission.grade = body.grade
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
            for submission in submissions:
                submission.student_info = submission.student.user_info
            return submissions
    
    async def upload(self, filename: str, assignment_id: str, user_id: str, file_ext:str, db: Session):
        pdf = open(filename, "rb")
        filename_in_s3 = f"{assignment_id}/{user_id}/{uuid.uuid4()}.{file_ext}"
        if file_ext not in ['pdf', 'jpg', 'jpeg', 'png']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File extension not supported")
        await object_storage_service.s3_upload(pdf.read(), filename_in_s3)
        pdf.close()
        return filename_in_s3
    
    async def check_submission(self, submission_id: str, db: Session):
        # client = OpenAI(api_key=settings.OPENAI_API_KEY)
        if not os.path.exists('services/temp'):
            os.makedirs('services/temp')

        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro-vision')
        # get pds submission from s3
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
        print(submission.file_urls)
        file_urls = eval(submission.file_urls)
        
        temp_file = await object_storage_service.s3_download(file_urls[0])
        # save pdf locally
        with open(f"services/temp/{file_urls[0]}", "wb") as f:
            f.write(temp_file)
            
        print(f"services/temp/{submission.file_urls}")
        # images = convert_from_path(f"services/temp/{submission.file_urls}")
        images = convert_from_path(f'services/temp/{submission.file_urls[0]}')
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
        for i in range(len(images2)):
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
                    glm.Part(text="Check the submitted work based on the provided answers, and provide detailed feedback and final mark. REPLY IN RUSSIAN."),
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
            generation_config=genai.types.GenerationConfig(
            max_output_tokens=100),
            stream=True)
        response.resolve()
        print(response.text)
        return response.text
    
    async def check_submission_gpt(self, submission_id: str, db: Session):
        # ... rest of your code ...
        # client = OpenAI(api_key=settings.OPENAI_API_KEY)
        if not os.path.exists('services/temp'):
            os.makedirs('services/temp')

        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        # get pds submission from s3
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
        print(submission.file_urls)
        file_urls = eval(submission.file_urls)
        pdf = await object_storage_service.s3_download(file_urls[0])
        # save pdf locally
        pdf_filename = file_urls[0].replace('/', '_')
        with open(f"services/temp/{pdf_filename}", "wb") as f:
            f.write(pdf)
        
            
        print(f"services/temp/{pdf_filename}")
        # images = convert_from_path(f"services/temp/{submission.file_urls}")
        images = convert_from_path(f'services/temp/{pdf_filename}')
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
        for i in range(len(images2)):
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
        # Initialize OpenAI API
        openai.api_key = settings.OPENAI_API_KEY

        # # Convert images to base64
        with open('vertical_assignment.jpg', 'rb') as f:
            assignment_image_base64 = base64.b64encode(f.read()).decode('utf-8')
        with open('vertical_submission.jpg', 'rb') as f:
            submission_image_base64 = base64.b64encode(f.read()).decode('utf-8')

        # Generate prompt
        # prompt = f"Check the submitted work based on the provided answers, and provide detailed feedback and final mark. REPLY IN RUSSIAN.\n\n[Assignment Image]\n{assignment_image_base64}\n\n[Submission Image]\n{submission_image_base64}"

        # # Call OpenAI API
        # response = openai.Completion.create(
        #     engine="text-davinci-002",
        #     prompt=prompt,
        #     max_tokens=500
        # )

        transcribed_submission = model.generate_content(
            
            glm.Content(
                parts = [
                    glm.Part(text="First count how many answers are there, based on this count list all of the answers of the student, just the answers, if student couldnt solve or omitted the problem indicate that. REPLY IN RUSSIAN."),
                    glm.Part(
                        inline_data=glm.Blob(
                            mime_type='image/jpeg',
                            data=pathlib.Path('vertical_submission.jpg').read_bytes()
                        )
                    ),
                    
                ],
            ),
            # generation_config=genai.types.GenerationConfig(
            # max_output_tokens=0),
            stream=True)
        transcribed_submission.resolve()
        print(transcribed_submission.text)
        assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
        assignment_problems = assignment.problems
        assignment_answers = assignment.answers
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
        model="gpt-4o",
                messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "First of all be sure to pay attention on student's answers and the correct answer list. Last image is the image with assignement and correct answers. Check the submitted work based on the provided answers, and provide detailed feedback and final mark. DONT FORGET TO PROVIDE FINAL MARK, IF ANY OF THE PROBLEMS OR QUESTIONS LEFT UNANSWERED IT MEANS NO POINT FOR THAT OR JUST INCORRECT ANSWER. REPLY IN RUSSIAN.",
                },
                {
                "type": "text",
                "text": f"Here is the transcribed solution of the student: {transcribed_submission.text}",
                },
                {
                "type": "image_url",
                "image_url": {
                   "url": f"data:image/jpeg;base64,{submission_image_base64}",
                },
                },
                {
                "type": "text",
                "text": f"Here are the assignment problems: {assignment_problems}, and here are the assignment answers: {assignment_answers}",
                },
                # {
                # "type": "image_url",
                # "image_url": {
                #    "url": f"data:image/jpeg;base64,{assignment_image_base64}",
                # },
                # },
            ],
            }
        ],
        #max_tokens=800, HHH
        )
        submission.ai_commentary = response.choices[0].message.content
        db.commit()
        db.refresh(submission)
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    
    async def transcribe(self, submission_id: str, db: Session):
        # ... rest of your code ...
        # client = OpenAI(api_key=settings.OPENAI_API_KEY)
        if not os.path.exists('services/temp'):
            os.makedirs('services/temp')

        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        # get pds submission from s3
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
        print(submission.file_urls)
        file_urls = eval(submission.file_urls)
        pdf = await object_storage_service.s3_download(file_urls[0])
        # save pdf locally
        pdf_filename = file_urls[0].replace('/', '_')
        with open(f"services/temp/{pdf_filename}", "wb") as f:
            f.write(pdf)
        
        filename = f"services/temp/{pdf_filename}"
        print(f"services/temp/{pdf_filename}")
        # images = convert_from_path(f"services/temp/{submission.file_urls}")
        if pdf_filename.endswith('.pdf'):
            
            # images = convert_from_path(f"services/temp/{submission.file_urls}")
            images = convert_from_path(f'services/temp/{pdf_filename}')
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
            filename = 'vertical_submission.jpg'

        with open(filename, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        # cleanup temp directories after jpgs are generated
        
        # Initialize OpenAI API
        # openai.api_key = settings.OPENAI_API_KEY

        chain = ChatGoogleGenerativeAI(
                    google_api_key=settings.GOOGLE_API_KEY,
                    model="gemini-1.5-flash",
                    temperature=1,
                    max_tokens=None,
                    timeout=None,
                    max_retries=2,
                    # other params...
                )

        # Generate prompt
        # prompt = f"Check the submitted work based on the provided answers, and provide detailed feedback and final mark. REPLY IN RUSSIAN.\n\n[Assignment Image]\n{assignment_image_base64}\n\n[Submission Image]\n{submission_image_base64}"

        # # Call OpenAI API
        # response = openai.Completion.create(
        #     engine="text-davinci-002",
        #     prompt=prompt,
        #     max_tokens=500
        # )
        ocrs = []
        for _ in range(3):
            msg = chain.invoke(
            [
                AIMessage(content="You are a useful bot that is especially good at extracting texts from images, no matter if handwritten or printed."),
                HumanMessage(
                    content=[
                        {"type": "text", "text": "Extract all texts from image. Take into consideration that most of the text and math symbols will be in Russian! Don't leave anything out, return all extracted texts with no comments."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                            },
                        },
                    ]
                )
            ]
            )
            ocrs.append(msg.content)
        #{"image_base64": image_base64, "text": msg.content}
        for idx, ocr in enumerate(ocrs):
            print(f"OCR version {idx + 1}: {ocr}")

        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        system_message = {
            "role": "system",
            "content": "You are a helpful assistant that formats text."
        }
        user_message = {
            "role": "user",
            "content": f"""Given these 3 OCR text versions of the same image: 
            1) {ocrs[0]}, 2) {ocrs[1]}, 2) {ocrs[2]}
            choose the most cohesive and logical elements to create the best OCR text.
            Make sure signs and words make sense logically.
            Do not add any comments, just return the best OCR you think of."""
        }
        response = model.generate_content(
            glm.Content(
                parts = [
                glm.Part(text=f"You are a helpful assistant that formats text.Given these 3 OCR text versions of the same image: 1) {ocrs[0]}, 2) {ocrs[1]}, 2) {ocrs[2]} choose the most cohesive and logical elements to create the best OCR text. Make sure signs and words make sense logically. Do not add any comments, just return the best OCR you think of. Return in the UNICODE format. NOT IN LATEX."),
                ],
            ),
           stream=True)
        shutil.rmtree('services/temp')
        try:
            response.resolve()
            result = LatexNodes2Text().latex_to_text(response.text)
            return result
        except:
            return await self.transcribe_gpt(submission_id, db)
        return 0
        # transcribed_submission = model.generate_content(
            
        #     glm.Content(
        #         parts = [
        #             glm.Part(text="Transcribe the student's submission."),
        #             glm.Part(
        #                 inline_data=glm.Blob(
        #                     mime_type='image/jpeg',
        #                     data=pathlib.Path(filename).read_bytes()
        #                 )
        #             ),
                    
        #         ],
        #     ),
        #     # generation_config=genai.types.GenerationConfig(
        #     # max_output_tokens=0),
        #     stream=True)
        # shutil.rmtree('services/temp')
        # try: 
        #     transcribed_submission.resolve()
        #     transcribed_submission = transcribed_submission.text
        # except:
        #     transcribed_submission = await self.transcribe_gpt(submission_id, db)
        # return transcribed_submission
    
    
    async def transcribe_gpt(self, submission_id: str, db: Session):
        print("here in transcribe gpt")
        if not os.path.exists('services/temp'):
            os.makedirs('services/temp')

        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        # get pds submission from s3
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
        print(submission.file_urls)
        file_urls = eval(submission.file_urls)
        pdf = await object_storage_service.s3_download(file_urls[0])
        # save pdf locally
        pdf_filename = file_urls[0].replace('/', '_')
        with open(f"services/temp/{pdf_filename}", "wb") as f:
            f.write(pdf)
        filename = f"services/temp/{pdf_filename}"
        if pdf_filename.endswith('.pdf'):
            
            print(f"services/temp/{pdf_filename}")
            # images = convert_from_path(f"services/temp/{submission.file_urls}")
            images = convert_from_path(f'services/temp/{pdf_filename}')
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
            
            filename = 'vertical_submission.jpg'
        # cleanup temp directories after jpgs are generated

        # Initialize OpenAI API
        openai.api_key = settings.OPENAI_API_KEY

        with open(filename, 'rb') as f:
            submission_image_base64 = base64.b64encode(f.read()).decode('utf-8')
        chain = ChatOpenAI(openai_api_key=settings.OPENAI_API_KEY,
                            model_name="gpt-4o",
                            temperature=1)
        ocrs = []
        for _ in range(3):
            msg = chain.invoke(
            [
                AIMessage(content="You are a useful bot that is especially good at extracting texts from images, no matter if handwritten or printed."),
                HumanMessage(
                    content=[
                        {"type": "text", "text": "Extract all texts from image. Take into consideration that most of the text and math symbols will be in Russian! Don't leave anything out, return all extracted texts with no comments. Don't reply in LaTeX, always respond in Unicode characaters."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{submission_image_base64}",
                            },
                        },
                    ]
                )
            ]
            )
            ocrs.append(msg.content)
        #{"image_base64": image_base64, "text": msg.content}
        for idx, ocr in enumerate(ocrs):
            print(f"OCR version {idx + 1}: {ocr}")

        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        system_message = {
            "role": "system",
            "content": "You are a helpful assistant that formats text."
        }
        user_message = {
            "role": "user",
            "content": f"""Given these 3 OCR text versions of the same image: 
            1) {ocrs[0]}, 2) {ocrs[1]}, 2) {ocrs[2]}
            choose the most cohesive and logical elements to create the best OCR text.
            Make sure signs and words make sense logically.
            Do not add any comments, just return the best OCR you think of."""
        }   
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=1,
            messages=[system_message, user_message]
        )
        
        text = response.choices[0].message.content
        result = LatexNodes2Text().latex_to_text(text)
        print(f"RAW OCR: {msg.content}\nProcessed OCR: {text}")
        shutil.rmtree('services/temp')
        return result
        # return response.choices[0].message.content
    def save_transcription(self, submission_id: str, transcription: str, db: Session):
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
        submission.transcription = transcription
        db.commit()
        db.refresh(submission)
        return submission
    
    def get_transcription(self, submission_id: str, db: Session):
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
        if submission:
            return submission.transcription
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    async def check_submission_from_transcription(self, submission_id: str, db: Session):
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
        assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
        assignment_problems = assignment.problems
        assignment_answers = assignment.answers
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
        model="gpt-4o",
                messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "First of all be sure to pay attention on student's answers and the correct answer list. Last image is the image with assignement and correct answers. Check the submitted work based on the provided answers, and provide detailed feedback and final mark. DONT FORGET TO PROVIDE FINAL MARK, IF ANY OF THE PROBLEMS OR QUESTIONS LEFT UNANSWERED IT MEANS NO POINT FOR THAT OR JUST INCORRECT ANSWER. REPLY IN RUSSIAN.",
                },
                {
                "type": "text",
                "text": f"Here is the transcribed solution of the student: {submission.transcription}",
                },
                {
                "type": "text",
                "text": f"Here are the assignment problems: {assignment_problems}, and here are the assignment answers: {assignment_answers}",
                },
                # {
                # "type": "image_url",
                # "image_url": {
                #    "url": f"data:image/jpeg;base64,{assignment_image_base64}",
                # },
                # },
            ],
            }
        ],
        max_tokens=800,
        )
        # set the ai_commentary of the submission to response
        submission.ai_commentary = response.choices[0].message.content
        db.commit()
        db.refresh(submission)
        return response.choices[0].message.content

    def get_submission_by_id(self, db: Session, assignment_id: str, user_id: str) -> AssignmentSubmission:
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == assignment_id).first()
        user = db.query(ClassroomUser).filter(ClassroomUser.user_id == user_id).first()
        if user.role == "teacher":
            teacher_classrooms = classroom_users_service.get_teacher_classrooms(db, user_id)
            assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
            if assignment.classroom_id not in [classroom.id for classroom in teacher_classrooms]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Teacher is not in the classroom of the assignment")
            submission.student_info = submission.student.user_info
            return submission
        else:
            if submission:
                if submission.student_id == user_id:
                    return submission
                else:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have access to this submission")
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
            
    def get_by_id(self, db: Session, assignment_id: str, user_id: str) -> AssignmentSubmission:
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.assignment_id == assignment_id).first()
        if submission:
            if submission.student_id == user_id:
                submission.student_info = submission.student.user_info
                return submission
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have access to this submission")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found") 

    def download(self, submission_id: str, user_id: str, db: Session):
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()

        classroom_user = db.query(ClassroomUser).filter(ClassroomUser.user_id ==  user_id, ClassroomUser.classroom_id==submission.assignment.classroom_id).first()
        file_urls = eval(submission.file_urls)
        if submission:
            if classroom_user:
                if classroom_user.role == "teacher":
                    
                    pdf = object_storage_service.s3_download(file_urls[0])
                    print(file_urls[0])
                    filename = file_urls[0].split('/')[-1]
                    return pdf, filename
            if submission.student_id == user_id:
                pdf = object_storage_service.s3_download(file_urls[0])
                filename = file_urls[0].split('/')[-1]
                print(file_urls[0])
                return pdf, filename
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
        
assignment_submission_service = AssignmentSubmissionService(AssignmentSubmission)
