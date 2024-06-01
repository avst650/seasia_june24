import os 
from apikey import apikey 

import streamlit as st 
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain 
from langchain.chains import LLMChain, SequentialChain
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
    input_variables = ['profile'], 
    template='analyze all the technical skills of this resume {profile}'
)
title_template2 = PromptTemplate(
    input_variables = ['skills'],
    template='based on these analyzed technical {skills} what technical refrence check questions should be asked according to this job description' + promptJD
)

# Llms
llm = OpenAI(temperature=0.9) 
title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True, output_key='skills')
title_chain2 = LLMChain(llm=llm, prompt=title_template2, verbose=True, output_key='questions')

sequential_chain = SequentialChain(chains=[title_chain, title_chain2], input_variables=['profile'], output_variables=['skills', 'questions'],verbose=True)

# Show stuff to the screen if there's a prompt
if promptJD and resume: 
    response = sequential_chain({'profile': resume})
    st.write(response['skills'])
    st.write(response['questions'])
