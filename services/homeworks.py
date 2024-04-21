from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, status, Header
from core import settings


# completion = client.chat.completions.create(
#   model="gpt-4-turbo",
#   messages=[
#     {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#     {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
#   ]
# )


async def generate_homework(subject, topic, grade_level, difficulty, quantity, extra_info=None):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    # client = openai.ChatCompletion.create(
    #     model="gpt-4-turbo",
    #     messages=[
    #         {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}."},
    #         {"role": "user", "content": f"Generate a {topic} homework."}
    #     ]
    # )

    if subject.lower() == 'mathematics':
        # Generate answers
        if extra_info is not None:
            answers = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. Also account for this: {extra_info}"},
                    {"role": "user", "content": f"Generate answers for which could be used for {topic} problems. Only provide a python list (e.g [1,2,3]) of {quantity} answers and NOTHING ELSE!"}
                ]
            )

            problems = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. Also account for this: {extra_info}"},
                    {"role": "user", "content": f"Generate problems for {topic} based on these answers: {answers.choices[0].message.content}."}
                ]
            )
        else:
            answers = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}."},
                    {"role": "user", "content": f"Generate answers for which could be used for {topic} problems. Only provide a python list (e.g [1,2,3]) of {quantity} answers and NOTHING ELSE!"}
                ]
            )

            # Generate problems based on answers
            problems = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are an AI tutor specializing in {subject} for {grade_level} grade. The difficulty level is {difficulty}. You only provide a list of problems, without including answers"},
                    {"role": "user", "content": f"Generate problems for {topic} based on these answers: {answers.choices[0].message.content}."}
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

# print(generate_homework('math', 'addition', '3rd', 'easy'))
