from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, status, Header
from core import settings
from .base import ServiceBase
from models import Assignment
from schemas import AssignmentCreate, AssignmentUpdate, HomeworkAssignmentCreate
from datetime import datetime
from .object_storage import object_storage_service
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import uuid
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import markdown2
import pdfkit
from jinja2 import Environment, FileSystemLoader


class AssignmentService(ServiceBase[Assignment, AssignmentCreate, AssignmentUpdate]):

    async def generate_homework(self, subject: str, topic, grade_level, difficulty, quantity, user_id, extra_info=None):

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        if subject.lower() == 'mathematics':
            # Generate answers
            if extra_info is not None:
                # answers = client.chat.completions.create(
                #     model="gpt-4-turbo",
                #     messages=[
                #         {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. Also account for this: {extra_info}"},
                #         {"role": "user", "content": f"Generate answers for which could be used for {topic} problems. Only provide a python list (e.g [1,2,3,...]) of {quantity} answers and NOTHING ELSE!"}
                #     ]
                # )

                # problems = client.chat.completions.create(
                #     model="gpt-4-turbo",
                #     messages=[
                #         {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of problems, without including answers. Also account for this: {extra_info}"},
                #         {"role": "user", "content": f"Generate problems for {topic} based on these answers: {answers.choices[0].message.content}. DON'T FORGET TO NUMERATE PROBLEMS! Quantity of problems: {quantity}"}
                #     ]
                # )

                # Generate problems based on answers
                problems = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of problems, without including answers. Also account for this: {extra_info}"},
                        {"role": "user", "content": f"Generate problems for {topic} DON'T FORGET TO NUMERATE PROBLEMS! Quantity of problems: {quantity}"}
                    ]
                )

                answers = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of answers. Also account for this: {extra_info}"},
                        {"role": "user", "content": f"Provide answers for these problems: {problems.choices[0].message.content}. Only provide a python list (e.g [1,2,3, \"2x\"...]) of answers and NOTHING ELSE!, DO NOT FORGET TO ENCLOSE ALL ANSWERS IN QUOTES!"}
                    ]
                )
            else:
                

                # Generate problems based on answers
                problems = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of problems, without including answers."},
                        {"role": "user", "content": f"Generate problems for {topic} DON'T FORGET TO NUMERATE PROBLEMS! Quantity of problems: {quantity}"}
                    ]
                )

                answers = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of answers"},
                        {"role": "user", "content": f"Provide answers for these problems: {problems.choices[0].message.content}. Only provide a python list (e.g [1,2,3, ...]) of answers and NOTHING ELSE!"}
                    ]
                )

            # # Solve problems and compare with answers
            # solutions = client.chat.completions.create(
            #     model="gpt-4-turbo",
            #     messages=[
            #         {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}."},
            #         {"role": "user", "content": f"Solve these problems: {problems}."}
            #     ]
            # )

            return {"problems": problems.choices[0].message.content, 
                    "answers": answers.choices[0].message.content,
                    "user_id": user_id}

        else:
            if extra_info is not None:
                client = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}."},
                        {"role": "user", "content": f"Generate a {topic} homework. Also account for this: {extra_info}"}
                    ]
                )
            else:
                client = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}."},
                        {"role": "user", "content": f"Generate a {topic} homework."}
                    ]
                )
            return {"problems": client.choices[0].message.content}
        


    def generate_pdf_from_homework(self, problems, answers, subject):
        filename = f"{subject}_{datetime.now()}_homework.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        # Write problems
        c.setFont("Helvetica", 12)
        c.drawString(30, height - 50, "Problems:")
        textobject = c.beginText()
        textobject.setTextOrigin(30, height - 70)
        textobject.setFont("Helvetica", 10)
        for problem in problems:
            textobject.textLine(problem)
        c.drawText(textobject)

        # Write answers
        c.setFont("Helvetica", 12)
        c.drawString(30, height - 120, "Answers:")
        textobject = c.beginText()
        textobject.setTextOrigin(30, height - 140)
        textobject.setFont("Helvetica", 10)
        for answer in answers:
            textobject.textLine(answer)
        c.drawText(textobject)

        c.save()   
        return filename
    
    def generate_pdf(self, problems, answers, output_filename='homework.pdf'):
        # Convert markdown problems to HTML
        html_problems = markdown2.markdown(problems)
        
        # Prepare the answers list from the string
        answers_list = eval(answers)
        
        # Load template
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('template.html')
        
        # Render the template with problems and answers
        rendered_html = template.render(problems=html_problems, answers=answers_list)
        
        # Convert to PDF
        pdfkit.configuration(wkhtmltopdf='/opt/bin/wkhtmltopdf')
        pdfkit.from_string(rendered_html, output_filename)

        print(f'PDF generated: {output_filename}')
        return output_filename
    
    async def upload_pdf_to_s3(self, filename):
        # get the file from the local storage
        file = open(filename, 'rb')
        # upload the file to s3 as bytes
        filename = "homeworks/" + uuid.uuid4().hex + ".pdf"
        print(2)
        await object_storage_service.s3_upload(file.read(), filename)
        print(2.5)
        return filename

    def create_homework(self, db: Session,
               obj_in: AssignmentCreate, pdf_url: str):
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data['pdf_url'] = pdf_url
        obj_in_data['id'] = str(uuid.uuid4())
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.flush()
        
        return db_obj
    
    async def approve_homework(self, homework: HomeworkAssignmentCreate, db: Session):
        # Generate pdf from problems and answers
        pdf = self.generate_pdf(homework.problems, homework.answers)
        # Upload pdf to s3
        filename = await self.upload_pdf_to_s3(pdf)
        return self.create_homework(db, homework.assignment, filename)
    

    # def save_homework_to_db(self, problems, answers, subject, date_from: datetime, date_to: datetime, description: str, max_grade: float, name: str, db):
    #     pdf = self.generate_pdf_from_homework(problems, answers, subject)
    #     assignment = Assignment(type='homework', date_from=date_from, date_to=date_to, description=description, pdf_url=pdf, max_grade=100, name=max_grade, name=name, created_at=datetime.now(), updated_at=datetime.now())
    #     db.add(assignment)
    #     db.commit()
    #     return assignment

assignment_service = AssignmentService(Assignment)