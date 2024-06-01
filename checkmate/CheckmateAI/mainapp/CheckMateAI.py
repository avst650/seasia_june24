import os 
import openai

import streamlit as st
import PyPDF2

openai.api_key  = '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'
def completeion(prompt, model='gpt-3.5-turbo'):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model = model,
        messages = messages,
        temperature = 0 #known as degree of randomness
    )
    return response.choices[0].message['content']

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    num_pages = len(pdf_reader.pages)
    text = ""

    for page in range(num_pages):
        page_obj = pdf_reader.pages[page]
        text += page_obj.extract_text()

    return text


def get_details():
    text = ""
    uploaded_file = st.file_uploader("Upload candidates Resume as PDF", type="pdf")
    if uploaded_file is not None:
        text = extract_text_from_pdf(uploaded_file)
    return text

resume = get_details()
promptJD = st.text_input('Plug in JD here')

prompt = f"""
Your task is to help a hiring HR team create a 
list for refrence check questions that must be asked 
at the time of interviewing a candidate for a job based on a resume provided.

Write a list of refrence check questions based on the information 
provided in the resume delimited by 
triple backticks and job description delimited by triple backticks.

The list of questions is intended for interview, 
so it should contain 5 technical in nature questions according to the required technical skills mentioned in the job description,
5 questions should be regarding the experience mentioned in the resume,
2 questions should focus on checking the educational background,
4 questions should be there irrespective of the the candidates resume but are improtant to ask at the time of interview as per the experince in the resume and 
job description mentioned
and 3 question should be for the person who has given the reference of this resume if it is mentioned in the resume
and focus on creating most revlevent question as per the resume.

The complexity of the questions should change as per the experience level mentioned in the resume varries 

The output should be in a json format
Resume: ```{resume}```
Job Description: ```{promptJD}```
"""

# if resume:
#     response = completeion(prompt4)
#     if response:
#         res = eval(response)
#     st.write(res)

if resume and promptJD:
    response = completeion(prompt)
    res = eval(response)

# Export the variable to another Python file
    with open('Questions.py', 'w') as file:
        file.write(f"response = {repr(res)}")



