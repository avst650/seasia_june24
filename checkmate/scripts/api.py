from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os 

app = FastAPI()

openai.api_key  = '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'

def completeion(prompt, model='gpt-3.5-turbo'):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model = model,
        messages = messages,
        temperature = 0 #known as degree of randomness
    )
    return response.choices[0].message['content']

class jd(BaseModel):
    jobdescription: str

@app.post('/')
async def questions(item:jd):
    jdobj = item.dict().items()
    
    prompt = f"""

Suppose you're working in a company where you hire candidates. You get a reference from your employee in your company.
Your task is to ask a list of reference check questions specifically for the person providing the referral.
These questions should be related to the job description provided and should help assess the suitability of the
referred candidate for the job opening.

Generate a list of atleast 12 reference check questions that should be asked to the person referring the candidate for 
the job opening based on the information provided in the job description delimited by triple backticks.

The questions should focus on the candidate's relevant skills, experience, and qualifications, and should check if the candidate's 
potential fit for the job.

The output should in json format.

job description: ```{jdobj}```
                
"""
    
    response = completeion(prompt)
    res = eval(response)
    return res
