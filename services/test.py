import markdown2
import pdfkit
from jinja2 import Environment, FileSystemLoader

def generate_pdf(problems, answers, output_filename='homework.pdf'):
    # Convert markdown problems to HTML
    html_problems = markdown2.markdown(problems)
    
    # Prepare the answers list from the string
    answers_list = eval(answers)
    
    # Load template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    
    # Render the template with problems and answers
    rendered_html = template.render(problems=html_problems, answers=answers_list)
    
    # Convert to PDF
    pdfkit.from_string(rendered_html, output_filename)

    print(f'PDF generated: {output_filename}')


# Sample usage
problems_md = """
### Problem 1
Solve for \(x\): \(x^2 - 4x + 4 = 0\)

### Problem 2
Calculate the derivative: \(\\frac{d}{dx}(x^3 - 2x + 1)\)
"""
problems_latex = "['Solve for \(x\): \(x^2 - 4x + 4 = 0\)', 'Calculate the derivative: \(\\frac{d}{dx}(x^3 - 2x + 1)\)']"

answers = "['x = 2', '3x^2 - 2']"

generate_pdf(problems_md, answers)