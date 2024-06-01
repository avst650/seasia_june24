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

# def completeion(prompt, model='gpt-3.5-turbo'):
#     messages = [{"role": "user", "content": prompt}]
#     response = openai.ChatCompletion.create(
#         model = model,
#         messages = messages,
#         temperature = 0 #known as degree of randomness
#     )
#     return response.choices[0].message['content']

# def extract_text_from_pdf(file):
#     pdf_reader = PyPDF2.PdfReader(file)
#     num_pages = len(pdf_reader.pages)
#     text = ""

#     for page in range(num_pages):
#         page_obj = pdf_reader.pages[page]
#         text += page_obj.extract_text()

#     return text


# def get_details():
#     text = ""
#     uploaded_file = st.file_uploader("Upload candidates Resume as PDF", type="pdf")
#     if uploaded_file is not None:
#         text = extract_text_from_pdf(uploaded_file)
#     return text

# resume = get_details()

promptJD = st.text_input('Plug in JD here')

prompt = f"""
Your task is to help a hiring HR team create a 
list for refrence check questions that must be asked 
at the time of interview based on a job description provided.

Write a list of refrence check questions based on the information 
provided in the job description delimited by 
triple backticks.

The list of questions is intended for interview, 
so should be technical in nature and focus on
creating most revlevent question as per the job description.

job description: ```{promptJD}```
"""

# if resume:
#     response = completeion(prompt4)
#     if response:
#         res = eval(response)
#     st.write(res)

if promptJD:
    response = completeion(prompt)

# Export the variable to another Python file
    with open('Questions.py', 'w') as file:
        file.write(f"response = {repr(response)}")



