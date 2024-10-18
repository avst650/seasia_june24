from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.docstore.document import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
from langchain_community.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
import datetime
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories.postgres import PostgresChatMessageHistory
import psycopg2
import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chains.question_answering import load_qa_chain
import json
import pandas as pd
from starlette.requests import Request


#############################
app = FastAPI()

class ReviewRequest(BaseModel):
    common_id: str

class ReviewResponse(BaseModel):
    query: str
    common_id: str

def get_message_history_db(session_id, db ="postgres"):
    connection_string = "postgres://postgres:KS4pBcm9MfHuy@database-1.c7o0o6mq64fi.us-east-1.rds.amazonaws.com:5432/db_ra"
    message_history = PostgresChatMessageHistory(session_id=session_id, connection_string=connection_string)
    return message_history    

def date_set(review_dates):
    if not review_dates:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=6)
    else:
        start_date, end_date = review_dates.split(" to ")
    
    if isinstance(start_date, datetime.date):
        start_date = start_date.strftime("%Y-%m-%d")
    if isinstance(end_date, datetime.date):
        end_date = end_date.strftime("%Y-%m-%d")
    return start_date, end_date  

df = pd.read_csv('responses.csv', sep=':', header=None, names=['greetings', 'responses'])

def search_csv(input_greeting):
    match = df[df['greetings'].str.lower() == input_greeting.lower()]
    if not match.empty:
        return match.iloc[0, 1]
    else:
        return None
    
def query_sentiment(query):
    llm=OpenAI()
    response = llm("Tell me this question is whether Analytical or General if I provide my SQL review data. Give only one word answer." + query)
    return response.strip()    

# Load greetings from the CSV file for the condition
greetings = df['greetings'].str.lower()

def clean_text(text):
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [token.lower() for token in tokens if token.lower() not in stop_words and token.isalnum()]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(tokens)

# Load or initialize embeddings data from JSON file
embeddings_file = "embeddings.json"
if os.path.exists(embeddings_file):
    with open(embeddings_file, "r") as f:
        embeddings_data = json.load(f)
else:
    embeddings_data = {}

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=120)

model_name = "sentence-transformers/all-mpnet-base-v2"
encode_kwargs = {'normalize_embeddings': False}
embeddings = SentenceTransformerEmbeddings(model_name=model_name, encode_kwargs=encode_kwargs)  

@app.post("/get_review")
async def get_review(review_request: ReviewRequest):

    common_id = review_request.common_id

    conn = psycopg2.connect(database="db_ra", 
                user="postgres", 
                host='database-1.c7o0o6mq64fi.us-east-1.rds.amazonaws.com',
                password="KS4pBcm9MfHuy",
                port=5432)
    cur = conn.cursor()
    
    try:
        cur.execute("""
                SELECT a.restaurant_name, r.* FROM restaurant AS a
                JOIN review_duplicate2 AS r ON a.id = r.common_id
                WHERE a.id = %s;
                """, (common_id,))

        rows = cur.fetchall()
        if rows:        
            doc = []
            combined_text = []
            for row in rows:
                restaurant_name = row[0]
                review_date = row[13].strftime('%Y-%m-%d')
                document = f"id={row[1]}, review_type={row[2]}, review={row[4]}, food={row[5]}, drink={row[6]}, sentiment={row[7]}, food_sentiment={row[8]}, staff={row[9]}, drink_sentiment={row[10]}, service_sentiment={row[11]}, review_score={row[12]}, review_date={review_date}"
                doc.append(Document(page_content=document, metadata={"Restaurant_id": common_id, "Restaurant_name": restaurant_name, "Review_Date": review_date}))
            combined_text.extend(doc)
            splits = text_splitter.split_documents(combined_text)

            persist_directory = 'db22'
            collection_name = f'id_{common_id}' 

            # Check if embeddings exist for the common_id in the JSON file
            if common_id in embeddings_data:
                return (f'Embeddings already exist for the common_id: {common_id}')
            else:
                # Create vectordb if it does not exist 
                vectordb = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=persist_directory,collection_name=collection_name)
                vectordb.persist()

                # Save the common_id in the JSON file
                embeddings_data[common_id] = True
                with open(embeddings_file, "w") as f:
                    json.dump(embeddings_data, f)

                return (f'Embeddings Created for the common_id: {common_id}')
        else:
            raise HTTPException(status_code=404, detail=f"No review found for restaurant_id {common_id}")

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail="Database error occurred")

    finally:
        conn.close()

@app.post("/process_answer")
async def process_answer(review_response: ReviewResponse):
    query = review_response.query
    common_id = review_response.common_id
    
    if not any(greeting.lower() in query.lower() for greeting in greetings):

        query_sent = query_sentiment(query)
        if query_sent.lower() != 'analytical':
        
            if common_id in embeddings_data:
                persist_directory = 'db22'
                collection_name = f'id_{common_id}'

                conn = psycopg2.connect(database="db_ra", 
                    user="postgres", 
                    host='database-1.c7o0o6mq64fi.us-east-1.rds.amazonaws.com',
                    password="KS4pBcm9MfHuy",
                    port=5432)
                cur = conn.cursor()
                
                try:
                    cur.execute("""
                        SELECT a.restaurant_name, r.review, r.review_date FROM restaurant AS a
                        JOIN review_duplicate2 AS r ON a.id = r.common_id
                        WHERE a.id = %s;
                        """, (common_id,))

                    rows = cur.fetchall()

                    if rows:
                        doc = []
                        for row in rows:
                            review_date = row[2].strftime('%Y-%m-%d')
                            doc.append(Document(page_content=clean_text(row[1]), metadata={"Restaurant_id": common_id, "Restaurant_name": row[0], "Review_Date": review_date}))


                except psycopg2.Error as e:
                    raise HTTPException(status_code=500, detail="Database error occurred")

                finally:
                    conn.close()  

                # session_id = request.session.get("session_id", None)
                # if session_id is None:
                #         request.session["session_id"]="1234"   
                session_id = collection_name
                print(session_id)
                message_history = get_message_history_db(session_id,"postgres")

                vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings, collection_name=collection_name)
                retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 5})
                llm1 = HuggingFaceHub(repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                                    model_kwargs={"temperature": 0.1, "max_length": 2048},
                                    huggingfacehub_api_token='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')
                
                prompt_template = """
                    <s>[INST]
                    <<SYS>>
                    Greeting (G): Hello!, You are an expert Advance AI Assisstant Chatbot. 
                    Begin with a friendly and professional greeting, Interact with the user in a natural and informative way.
                    Identify Greetings: When a user initiates the conversation, identify if their message is a greeting (e.g., "Hi", "Hello").
                    Respond to Greetings: If the user's message is a greeting, respond with a pre-defined template like "Hi! How can I help you today?"
                    Continue Conversation: After responding to the greeting, if applicable, utilize my existing capabilities to understand and respond to the user's intent as instructed in the original prompt.

                    Context (C): Hi, You are an expert Advance AI Assisstant Chatbot presented with a text chunk referred 
                    to as context. This text is actually a reviews of different customers of different restaurants.
                    The text also contains the review date and restaurant name. Which is also an essential factor in Question-Answering.
                    
                    Objective (O): Your task is to scrutinize texts and its information. And you have to Only retrieve the information 
                    on the basis of restaurant_id pass earlier. 
                    **No need to answer on the Another restaurant. So only answer on the restaurant_id selected earlier by th user. 
                    Your task also includes to identify any segments that align with the provided query. 
                    This analysis includes semantic, thematic, and direct keyword matching. 
                    In cases of ambiguity, prioritize retaining information to ensure no vital content is missed.
                    
                    Style (S): Initially greet your user. The analysis should be conducted in a detailed, methodical manner, respecting the 
                    original structure and content of query.
                    
                    Tone (T): Maintain a professional tone throughout the analysis, focusing on precision and thoroughness.
                    
                    Audience (A): This task is designed for an expert AI model capable of complex text analysis and interpretation.
                    
                    Response Format (R): Produce a most relevant output that includes:
                    "Greeting:" Greet your user with "Hello! How can I assist you today?".
                    "Answer": segments of context that correspond to the query
                    "meaningful chunks": segments of context that correspond to the source_documents.
                    <<SYS>>

                    You MUST:
                    **You must use AI to generate a new greeting based on your instructions.**
                    **Strictly Don't response from your knowledge base.**
                    Think step by step as you analyze Answer.
                    You must reply within the information of passed restaurant_id only. If query from other restaurant is asked then strictly reply with "Ask query from your selected Restaurant only!."
                    Carefully match elements of source_documents with the provided query.
                    "Information Retrieve": Must check if particular restaurant mentioned in query. If mentioned check restaurant name in your context. If can;t get that name then strictly response with "Ask only for selected restaurant only."
                    Retain ambiguous cases to prevent loss of potentially relevant information.
                    Compile your findings into the well defined manner, ensuring all parts of answer are accounted for in their respective categories.
                    Also make the summary of the whole conversation and store it in {chat_history}
                    where
                        retriever = "{context}"
                        query = {question} 
                        <s>[/INST]
                        Answer: """
                
                prompt = PromptTemplate(template=prompt_template,
                                input_variables=['context','history', 'question'])
                
                memory = ConversationBufferMemory(llm=llm1,
                                                memory_key='chat_history',
                                                return_messages=True,
                                                output_key='answer')

                qa_chain = ConversationalRetrievalChain.from_llm(llm=llm1,
                                                                chain_type="map_reduce",
                                                                retriever=retriever,
                                                                memory=memory,
                                                                return_source_documents=True,
                                                                get_chat_history=lambda h: h,
                                                                verbose=False,
                                                                condense_question_prompt=prompt)

                generated_text = qa_chain(query)
                # response = generated_text['result']
                answer = f"{generated_text['chat_history'][-1].content}\n"
                response = answer.split("=========\nFINAL ANSWER:")[-1].strip()
                message_history.add_user_message(query)
                message_history.add_ai_message(response)
                # metadata = f"{generated_text['source_documents']}\n"

                return {"Answer": response}#, "Source_documents": metadata}
            else:
                return f"Collection not Avaialbe for common_id {common_id}"
        else:
            agent_function
    else:
        return search_csv(query)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
