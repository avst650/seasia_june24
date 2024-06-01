import os 
from apikey import apikey 

import streamlit as st 
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain 
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


def get_details():
    text = ""
    uploaded_file = st.file_uploader("Upload candidates Resume as PDF", type="pdf")
    if uploaded_file is not None:
        text = extract_text_from_pdf(uploaded_file)
    return text

resume = get_details()

promptJD = st.text_input('Plug in JD here')

# Prompt templates
title_template = PromptTemplate(
    input_variables = ['profile', 'jd'], 
    template='''As a recruting expert analyze all the technical skills of this resume {profile} and also analyze technical requirements 
                of this job description {jd} and based on you analysis of the both provide me with the refrence check 
                 question to ask to the candidate '''
)

# Llms
llm = OpenAI(temperature=0.9) 
title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True)

# Show stuff to the screen if there's a prompt
if promptJD and resume: 
    response = title_chain.run(profile=resume, jd=promptJD)
    st.write(response)
