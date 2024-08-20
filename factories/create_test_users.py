import requests
import json


def create_test_students(number_of_students):
    url = "http://localhost:8000/api/v1/users/students/register"
    headers = {
        'Content-Type': 'application/json'
    }
    for i in range(number_of_students):

        data = {
            "grade_level": 5,
            "guardian_phone_number": "777777777",
            "guardian_first_name": "string",
            "guardian_last_name": "string",
            "guardian_father_name": "string",
            "guardian_email": f"test_student_guardian{i}@example.com",
            "user": {
                "role": "student",
                "email": f"test_student{i}@example.com",
                "password_hash": "123456",
                "user_info": {
                    "first_name": f"Student{i}",
                    "last_name": f"lastname{i}",
                    "father_name": "string",
                    "address": "string",
                    "gender": True,  # Assuming True represents male, False would represent female
                    "phone_number": "string"
                }
            }
        }
        response = requests.request(
            "POST", url, headers=headers, data=json.dumps(data))
        print(response.text)
        print(response.status_code)
    return "Students created successfully"


def create_test_teachers(number_of_teachers):
    url = "http://localhost:8000/api/v1/users/teachers/register"
    headers = {
        'Content-Type': 'application/json'
    }
    for i in range(number_of_teachers):

        data = {
            "department_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "user": {
                "role": "teacher",
                "email": f"test_teacher{i}@example.com",
                "password_hash": "123456",
                "user_info": {
                    "first_name": f"Teacher{i}",
                    "last_name": f"lastname{i}",
                    "father_name": "string",
                    "address": "string",
                    "gender": True,  # Assuming True represents male, False would represent female
                    "phone_number": "77777777777"
                }
            }
        }
        response = requests.request(
            "POST", url, headers=headers, data=json.dumps(data))
        print(response.text)
        print(response.status_code)
    return "Teachers created successfully"

create_test_students(80)
create_test_teachers(80)