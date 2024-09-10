from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, status, Header, UploadFile, File
from core import settings
from .base import ServiceBase
from models import Assignment, ClassroomUser, Classroom, User
from schemas import AssignmentCreate, AssignmentUpdate, HomeworkAssignmentCreate, AssignmentsStudentsReadShort
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
from abc import ABC, abstractmethod
from enum import Enum

class TaskGenerator(ABC):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    @abstractmethod
    async def generate(self, **kwargs):
        pass

    async def call_openai_api(self, system_message: dict, user_message: dict):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[system_message, user_message]
        )

        if not response.choices:
            raise HTTPException(status_code=500, detail="Failed to generate tasks")

        return response.choices[0].message.content

class WordProblemGenerator(TaskGenerator):
    async def generate(self, subject: str, topic: str, num_questions: int, thematic: str = None, language: str = "russian"):
        system_message = {
            "role": "system",
            "content": f"You are an AI tutor specializing in {subject}. Always reply in {language}, even if the question is in another language.."
        }

        user_message = {
            "role": "user",
            "content": f"""
                    Generate {num_questions} word problems for the topic '{topic}'.
                    Each problem should follow the thematic if it was given: '{thematic}'.
                    Provide the correct answersw as well.
                    Don't write any extra comment.

                    Follow this format of response!!! It is critical that you follow this format:
                    ### Question 1:
                    text of question
                    ||| Answer 1:
                    ### Question 2:
                    text of question
                    ||| Answer 2:
                    and so on.
                    """
                }

        return await self.call_openai_api(system_message, user_message)


class MultipleChoiceQuestionGenerator(TaskGenerator):
    async def generate(self, subject: str, topic: str, grade_level: str, difficulty: str, num_questions: int, num_choices: int, extra_info: str = None, language: str = "russian"):
        system_message = {
            "role": "system",
            "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. Always reply in {language}, even if the question is in another language."
        }

        user_message = {
            "role": "user",
            "content": f"Generate {num_questions} multiple choice questions for the topic '{topic}' with {num_choices} choices each. At the end ALWAYS Provide the correct answer as well. Don't write any extra comment. Always reply in {language}, even if the question is in another language.{f'Additional instructions: {extra_info}' if extra_info else ''}"
        }

        return await self.call_openai_api(system_message, user_message)
    
class AssignmentService(ServiceBase[Assignment, AssignmentCreate, AssignmentUpdate]):
    def __init__(self, db: Session):
        super().__init__(db)
        self.word_problem_generator = WordProblemGenerator(api_key=settings.OPENAI_API_KEY)
        self.mcq_generator = MultipleChoiceQuestionGenerator(api_key=settings.OPENAI_API_KEY)
    
    async def generate_word_problems(self, subject_aim: str, topic: str, num_questions: int, thematic: str = None, language: str = "russian"):
        return {"word_problems": await self.word_problem_generator.generate(subject_aim, topic, num_questions, thematic, language)}

    async def generate_multiple_choice_questions(self, subject: str, topic: str, grade_level: str, difficulty: str, num_questions: int, num_choices: int, extra_info: str = None, language: str = "russian"):
        return {"questions": await self.mcq_generator.generate(subject, topic, grade_level, difficulty, num_questions, num_choices, extra_info, language)}

    async def generate_homework(self, subject: str, topic, grade_level, difficulty, quantity, user_id, extra_info=None, language="russian"):
        conditional_ib_statement = "You should comply with IB standards and practices."
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
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of problems, without including answers.Just provide the problems without any additional comments. Also account for this: {extra_info}. Always reply in {language}, even if the question is in another language. {conditional_ib_statement if language == 'english' else ''}"},
                        {"role": "user", "content": f"Generate problems for {topic} DON'T FORGET TO NUMERATE PROBLEMS! Quantity of problems: {quantity}"}
                    ]
                )

                answers = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of answers. Also account for this: {extra_info}. Always reply in {language}, even if the question is in another language.{conditional_ib_statement if language == 'english' else ''}"},
                        {"role": "user", "content": f"Provide answers for these problems: {problems.choices[0].message.content}. Only provide a python list (e.g [1,2,3, \"2x\"...]) of answers and NOTHING ELSE!, DO NOT FORGET TO ENCLOSE ALL ANSWERS IN QUOTES!"}
                    ]
                )
            else:
                

                # Generate problems based on answers
                problems = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. Just provide the problems without any additional comments. The difficulty level is {difficulty}. You only provide a list of problems, without including answers. Always reply in {language}, even if the question is in another language.{conditional_ib_statement if language == 'english' else ''}"},
                        {"role": "user", "content": f"Generate problems for {topic} DON'T FORGET TO NUMERATE PROBLEMS! Quantity of problems: {quantity}"}
                    ]
                )

                answers = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of answers. Always reply in {language}, even if the question is in another language.{conditional_ib_statement if language == 'english' else ''}"},
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
                """client = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. Always reply in russian, even if the question is in english."},
                        {"role": "user", "content": f"Generate a {topic} homework. Also account for this: {extra_info}"}
                    ]
                )"""

                problems = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of problems, without including answers. Also account for this: {extra_info}. Always reply in russian, even if the question is in english."},
                        {"role": "user", "content": f"Generate problems for {topic} DON'T FORGET TO NUMERATE PROBLEMS! Quantity of problems: {quantity}"}
                    ]
                )

                answers = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of answers. Also account for this: {extra_info}. Always reply in russian, even if the question is in english."},
                        {"role": "user", "content": f"Provide answers for these problems: {problems.choices[0].message.content}. Only provide a python list (e.g [1,2,3, \"2x\"...]) of answers and NOTHING ELSE!, DO NOT FORGET TO ENCLOSE ALL ANSWERS IN QUOTES!"}
                    ]
                )
                
            else:
                """client = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. Always reply in russian, even if the question is in english."},
                        {"role": "user", "content": f"Generate a {topic} homework."}
                    ]
                )"""

                problems = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of problems, without including answers. Always reply in russian, even if the question is in english."},
                        {"role": "user", "content": f"Generate problems for {topic} DON'T FORGET TO NUMERATE PROBLEMS! Quantity of problems: {quantity}"}
                    ]
                )

                answers = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of answers. Always reply in russian, even if the question is in english."},
                        {"role": "user", "content": f"Provide answers for these problems: {problems.choices[0].message.content}. Only provide a python list (e.g [1,2,3, ...]) of answers and NOTHING ELSE!"}
                    ]
                )
            return {"problems": problems.choices[0].message.content, 
                    "answers": answers.choices[0].message.content,
                    "user_id": user_id}
            #return {"problems": client.choices[0].message.content}
        


    # def generate_pdf_from_homework(self, problems, answers, subject):
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
    
    def generate_pdf(self, problems, answers, output_filename='homework.pdf'):
        # Convert markdown problems to HTML
        html_problems = markdown2.markdown(problems)
        
        # Prepare the answers list from the string
        if answers:
            try:
                answers_list = eval(answers)
            except:
                answers_list = answers.split('\n')
        else:
            answers_list = []
        # Load template
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('template.html')
        
        # Render the template with problems and answers
        rendered_html = template.render(problems=html_problems, answers=answers_list)
        
        # Convert to PDF
        # pdfkit.configuration(wkhtmltopdf='/opt/bin/wkhtmltopdf')
        pdfkit.from_string(rendered_html, output_filename)
        print(f'PDF generated: {output_filename}')
        return output_filename
    
    async def upload_pdf_to_s3(self, filename):
        # get the file from the local storage
        file = open(filename, 'rb')
        # upload the file to s3 as bytes
        # get file extension
        ext = filename.split('.')[-1]
        filename = "homeworks/" + uuid.uuid4().hex + "."+ext
        print(2)
        await object_storage_service.s3_upload(file.read(), filename)
        print(2.5)
        file.close()
        return filename
    

    def create_homework(self, db: Session,
               obj_in: HomeworkAssignmentCreate, pdf_url: str):
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data['pdf_url'] = pdf_url
        obj_in_data['id'] = str(uuid.uuid4())

        # remove problems and answers from the dict
        # if user_id is present as key, remove it
        if 'user_id' in obj_in_data:
            obj_in_data.pop('user_id')
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.flush()
        db_obj.file_extension = pdf_url.split('.')[-1]
        return db_obj
    
    async def approve_homework(self, homework: HomeworkAssignmentCreate, db: Session):
        # Generate pdf from problems and answers
        pdf = self.generate_pdf(homework.problems, homework.answers)
        # Upload pdf to s3
        filename = await self.upload_pdf_to_s3(pdf)
        return self.create_homework(db, homework, filename)
    
    async def create_from_pdf(self, body: AssignmentCreate, filename: str, db: Session):
        return self.create_homework(db, body, filename)
    
    def get_all_teacher_assignments(self, classroom_id: str, db: Session):
        return db.query(Assignment).filter(Assignment.classroom_id == classroom_id).all()
    
    def get_all_student_assignments(self, classroom_id: str, user_id: str, db: Session):
        assignments = db.query(Assignment).filter(Assignment.classroom_id == classroom_id).all()
        return [AssignmentsStudentsReadShort.from_orm(assignment) for assignment in assignments]


    # def save_homework_to_db(self, problems, answers, subject, date_from: datetime, date_to: datetime, description: str, max_grade: float, name: str, db):
    #     pdf = self.generate_pdf_from_homework(problems, answers, subject)
    #     assignment = Assignment(type='homework', date_from=date_from, date_to=date_to, description=description, pdf_url=pdf, max_grade=100, name=max_grade, name=name, created_at=datetime.now(), updated_at=datetime.now())
    #     db.add(assignment)
    #     db.commit()
    #     return assignment

    # def get_student_assignment(self, assignment_id: str, user_id: str, db: Session):
    #     assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    #     if assignment:
    #         return assignment
    #     else:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
        
    async def download_pdf_from_s3(self, assignment_id: str, user_id: str, db: Session):
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        classroom_user = db.query(ClassroomUser).filter(ClassroomUser.classroom_id == assignment.classroom_id, ClassroomUser.user_id == user_id).first()
        if classroom_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have access to this assignment")
        print(assignment.pdf_url)
        filename = assignment.pdf_url.split('/')[-1]
        return await object_storage_service.s3_download(assignment.pdf_url), filename
    
    def get_student_assignment(self, classroom_id: str, assignment_id: str, user_id: str, db: Session):
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        classroom_user = db.query(ClassroomUser).filter(ClassroomUser.classroom_id == classroom_id, ClassroomUser.user_id == user_id).first()
        if classroom_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have access to this assignment")
        return assignment
    
    def get_teacher_assignment(self, classroom_id: str, assignment_id: str, user_id: str, db: Session):
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        classroom_user = db.query(ClassroomUser).filter(ClassroomUser.classroom_id == classroom_id, ClassroomUser.user_id == user_id).first()
        if classroom_user is None or classroom_user.role != "teacher":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have access to this assignment")
        return assignment
    
    def delete(self, assignment_id: str, teacher_id: str, db):
        assignment = db.query(Assignment).filter(Assignment.id==assignment_id).first()

        if not assignment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
        
        classroom_user = db.query(ClassroomUser).filter(ClassroomUser.classroom_id == assignment.classroom_id, ClassroomUser.user_id == teacher_id).first()
        if not classroom_user or classroom_user.role != "teacher":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have access to this assignment")
        
        db.delete(assignment)
        db.commit()
        return "success"
    
    def create_test_classrooms_and_add_users(self, number_of_classrooms, db: Session):
        for i in range(number_of_classrooms):
            if i != 0:
                classroom = Classroom(
                    name=f"Classroom{i}",
                    subject_id="663365b2-8b48-4e21-800c-dadf52586986",
                    school_id="3fa85f64-5717-4562-b3fc-2c963f66afa6"
                )
                db.add(classroom)
                db.flush()
                test_teacher = db.query(User).filter(User.email == f"test_teacher{i}@example.com").first()
                test_student = db.query(User).filter(User.email == f"test_student{i}@example.com").first()
                classroom_user_teacher = ClassroomUser(
                    classroom_id=classroom.id,
                    user_id=test_teacher.id,
                    role="teacher"
                )
                classroom_user_student = ClassroomUser(
                    classroom_id=classroom.id,
                    user_id=test_student.id,
                    role="student"
                )
                db.add(classroom_user_teacher)
                db.add(classroom_user_student)
        db.commit()
        return "Classrooms created successfully"
    



assignment_service = AssignmentService(Assignment)