import os, shutil, requests, glob
from langchain.document_loaders import PyPDFLoader
from fastapi import  FastAPI, File, UploadFile, Request
import uvicorn
import os
import glob
from pathlib import Path

from typing import List
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain.chains import  RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain import OpenAI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.vectorstores import FAISS
import requests

import shutil
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from langchain.document_loaders import PyMuPDFLoader
from typing import List
from urllib.parse import urlparse
from pydantic import BaseModel
from pathlib import Path
from shutil import make_archive
from typing import List
from langchain.document_loaders import PDFPlumberLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain import OpenAI
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import  FastAPI, File, UploadFile, Request
import uvicorn
from langchain.schema.document import Document
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document


# Path to Tesseract executable (change this to your Tesseract installation path)
#tesseract_cmd_path = r'Tesseract-OCR/tesseract.exe'
#pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path

base_dir = os.getcwd()

if not os.path.exists(os.path.join(base_dir, 'save_pdf')):
    os.mkdir(os.path.join(base_dir, 'save_pdf'))


pdf_dir =os.path.join(base_dir, 'save_pdf')


os.environ["OPENAI_API_KEY"] = "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"    ## client api


app = FastAPI()
app.mount("/var/www/html/save_pdf", StaticFiles(directory="save_pdf"), name="static")
static_url='http://10.8.14.84/save_pdf/'

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# static_url='save_pdf/'
# Base_url='http://10.8.10.134:8000/'


class Item(BaseModel):
    pdf_path :List[str]
    question: str


@app.post("/uploadfile/")   
async def save_file_dir(uploaded_file: UploadFile = File(...)):
    file_location = f'/var/www/html/save_pdf/{uploaded_file.filename}'
    with open(file_location, "wb+") as file_object:
        file_object.write(uploaded_file.file.read())
    return {"info": f"file '{uploaded_file.filename}' saved at '{file_location}'"}


@app.get("/list_pdf")
async def list_files(request: Request):
    files = os.listdir('/var/www/html/save_pdf')
    lss=[f'{static_url}'+i for i in files]
    return lss

@app.post("/create_vector")
async def create_vec(item: Item):
    if os.path.exists(os.path.join(base_dir, 'temp')):
        shutil.rmtree(os.path.join(base_dir, 'temp'))

    if not os.path.exists(os.path.join(base_dir, 'temp')):
        os.mkdir(os.path.join(base_dir, 'temp'))
        
    pdf_folder_path = os.path.join(base_dir, 'temp','*')

    var = item.dict()
    pdf_urls = var['pdf_path']
    query = var['question']
    for pdf_url in pdf_urls:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            pdf_content = response.content
            pdf_path = Path(pdf_url)
            az = pdf_path.stem + pdf_path.suffix
            print(az)
            local_file_path = os.path.join(base_dir, 'temp',az)

            with open(local_file_path, "wb") as pdf_file:
                pdf_file.write(pdf_content)
                print(f"PDF downloaded and saved as {local_file_path}")
        else:
            print(f"Failed to download PDF. Status code: {response.status_code}")
            
    mt_data = []
    contexts = []
    for i in glob.glob(pdf_folder_path):
        print(i)
        loader = PyPDFLoader(i)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
        texts = text_splitter.split_documents(documents)
        print(texts,'kkkk')
        
        if texts == list():
            images = convert_from_path(i)
            doc =[]
            for page_number, image in enumerate(images, start=1):
                image = image.convert('L')
                text = pytesseract.image_to_string(image)
                doc.append( Document(page_content=text, metadata={"source":pdf_path, "page":page_number}))
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=10)
            texts=text_splitter.split_documents(doc)
            print(texts,'vvvvvvvvvvvvvvvv')
        
        try:
            # save in
            embedding = OpenAIEmbeddings()
            vectordb = FAISS.from_documents(documents=texts, embedding=embedding)
            retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 5})
            llm = OpenAI(temperature=0, model_name='text-davinci-003')

            prompt_template = """
        Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer
        
        context: {context}

        Question: from mentioned context, {question}

        Then write the query in answer form. Before answering the question just greet them.

        Write a brief and specific Answer in bullet form.

        If the answer is found in the database, only then give the answer.

        Write Answer from the context
        """

            PROMPT = PromptTemplate(
                template=prompt_template, input_variables=["context", "question"]
            )

            chain_type_kwargs = {"prompt": PROMPT}
            qa_interface = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever,
                                                       return_source_documents=True, chain_type_kwargs=chain_type_kwargs)
            result = qa_interface({"query": query})

            contexts.append(result['result'])
            page_numb=[]
            sour=[]
            for meta_data in result['source_documents']:
                source = Path(meta_data.metadata['source'])
                sourc = source.stem + source.suffix
                page_number = meta_data.metadata['page']
                page_numb.append(page_number+1)
                sour.append(sourc)
            mt_data.append({'page_no': list(set(page_numb)), 'source_path': list(set(sour))})

        except Exception as e:
            print(e)
            return {'error': 'Please check your PDF file again!'}
    
    return {'answer': contexts, 'meta_data': mt_data}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=24851)
