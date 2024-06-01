import os 
from apikey import apikey 

import streamlit as st 
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain 
import PyPDF2

os.environ['OPENAI_API_KEY'] = apikey


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

# Prompt templates
title_template = PromptTemplate(
    input_variables = ['profile'], 
    template='here is a resume {profile} what refrence check questions should i ask to this candidate plu also mention refrence check question to the candidates previous organizations'
)

# Llms
llm = OpenAI(temperature=0.9) 
title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True)

# Show stuff to the screen if there's a prompt
if resume: 
    response = title_chain.run(profile=resume)
    st.write(response)
