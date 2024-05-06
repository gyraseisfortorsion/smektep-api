import PIL.Image
import google.generativeai as genai


GOOGLE_API_KEY = ""

genai.configure(api_key=GOOGLE_API_KEY)
img = PIL.Image.open('image.jpg')
model = genai.GenerativeModel('gemini-pro-vision')
response = model.generate_content(["Write a short, engaging blog post based on this picture. It should include a description of the meal in the photo and talk about my journey meal prepping.", img], stream=True)
response.resolve()
print(response.text)