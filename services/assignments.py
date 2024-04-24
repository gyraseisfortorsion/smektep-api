from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, status, Header
from core import settings
from .base import ServiceBase
from models import Assignment
from schemas import AssignmentCreate, AssignmentUpdate
from datetime import datetime

# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas

class AssignmentService(ServiceBase[Assignment, AssignmentCreate, AssignmentUpdate]):

    async def generate_homework(subject, topic, grade_level, difficulty, quantity, extra_info):

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        if subject.lower() == 'mathematics':
            # Generate answers
            if extra_info is not None:
                answers = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. Also account for this: {extra_info}"},
                        {"role": "user", "content": f"Generate answers for which could be used for {topic} problems. Only provide a python list (e.g [1,2,3,...]) of {quantity} answers and NOTHING ELSE!"}
                    ]
                )

                problems = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of problems, without including answers. Also account for this: {extra_info}"},
                        {"role": "user", "content": f"Generate problems for {topic} based on these answers: {answers.choices[0].message.content}. DON'T FORGET TO NUMERATE PROBLEMS! Quantity of problems: {quantity}"}
                    ]
                )
            else:
                answers = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. Also account for this: {extra_info}"},
                        {"role": "user", "content": f"Generate answers for which could be used for {topic} problems. Only provide a python list (e.g [1,2,3, ...]) of {quantity} answers and NOTHING ELSE!"}
                    ]
                )

                # Generate problems based on answers
                problems = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of problems, without including answers. Also account for this: {extra_info}"},
                        {"role": "user", "content": f"Generate problems for {topic} based on these answers: {answers.choices[0].message.content}. DON'T FORGET TO NUMERATE PROBLEMS! Quantity of problems: {quantity}"}
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
                    "answers": answers.choices[0].message.content}

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
        


    # def generate_pdf_from_homework(problems, answers, subject):
    #     filename = f"{subject}_{datetime.now()}_homework.pdf"
    #     c = canvas.Canvas(filename, pagesize=letter)
    #     width, height = letter

    #     # Write problems
    #     c.setFont("Helvetica", 12)
    #     c.drawString(30, height - 50, "Problems:")
    #     textobject = c.beginText()
    #     textobject.setTextOrigin(30, height - 70)
    #     textobject.setFont("Helvetica", 10)
    #     for problem in problems:
    #         textobject.textLine(problem)
    #     c.drawText(textobject)

    #     # Write answers
    #     c.setFont("Helvetica", 12)
    #     c.drawString(30, height - 120, "Answers:")
    #     textobject = c.beginText()
    #     textobject.setTextOrigin(30, height - 140)
    #     textobject.setFont("Helvetica", 10)
    #     for answer in answers:
    #         textobject.textLine(answer)
    #     c.drawText(textobject)

    #     c.save()   
    #     return filename
    
    # def save_homework_to_db(self, problems, answers, subject, date_from: datetime, date_to: datetime, description: str, max_grade: float, name: str, db):
    #     pdf = self.generate_pdf_from_homework(problems, answers, subject)
    #     assignment = Assignment(type='homework', date_from=date_from, date_to=date_to, description=description, pdf_url=pdf, max_grade=100, name=max_grade, name=name, created_at=datetime.now(), updated_at=datetime.now())
    #     db.add(assignment)
    #     db.commit()
    #     return assignment