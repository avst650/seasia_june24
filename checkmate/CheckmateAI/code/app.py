import os 
from apikey import apikey 

import streamlit as st 
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain 
import PyPDF2

os.environ['OPENAI_API_KEY'] = apikey

st.set_page_config(
    page_title='Refrence CHeck'
)


def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    num_pages = len(pdf_reader.pages)
    text = ""

    for page in range(num_pages):
        page_obj = pdf_reader.pages[page]
        text += page_obj.extract_text()

    return text


uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

text = extract_text_from_pdf(uploaded_file)
resume = text

promptJD = st.text_input('Plug in JD here')

# Prompt templates
title_template = PromptTemplate(
    input_variables = ['profile', 'jd'], 
    template='analyze all the skills of {profile} and check if the profile has the experience according to this job description {jd} or not'
)

# Llms
llm = OpenAI(temperature=0.9) 
title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True)

# Show stuff to the screen if there's a prompt
if promptJD and resume: 
    response = title_chain.run(profile=resume, jd=promptJD)
    st.write(response)
