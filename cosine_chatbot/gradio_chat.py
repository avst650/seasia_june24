import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
import gradio as gr
from nltk.stem import PorterStemmer

# Preprocess function
def preprocess_text(text):
    words = nltk.word_tokenize(text) # tokenization
    words = [word.lower() for word in words] # lower case
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    stemmer = PorterStemmer() # stemming
    words = [stemmer.stem(word) for word in words]
    processed_text = ' '.join(words)
    return processed_text

# Function to get chatbot response
def get_intent(user_input, chat_history):
    preprocessed_input = preprocess_text(user_input) # get preprocessed text
    user_vector = tfidf_vectorizer.transform([preprocessed_input]) # convert natural language query to vectors
    similarities = cosine_similarity(user_vector, tfidf_matrix) # find most relevant questions in the data
    max_similarity = similarities.max()
    if max_similarity < 0.4: # if threshold is less than 40% then it means user asked out of context question
        intent = ''
        response = 'sorry, try again!'
    else:
        intent_index = similarities.argmax() 
        # intent = data['intent'][intent_index]
        response = data['answer'][intent_index] # find most relevant answer

    chat_history.append((user_input, response)) # response fetched
    return "", chat_history

# Load data from CSV
data = pd.read_csv('data.csv')

# NLTK resources
nltk.download('stopwords')
nltk.download('punkt')

# TF-IDF Vectorizer to vectorize all data
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(data['question'])

# gradio web UI interface
with gr.Blocks() as demo:
    gr.Markdown(
    """
    # QA ChatBot
    """)

    # chat display
    chatbot = gr.Chatbot(value=[["Hello Sir. I can assist you in speciality domains like plumber, carpentry, electrician.",
                                  "You can ask me queries related to these domains."]])
    
    msg = gr.Textbox() # text box for input query
    clear = gr.ClearButton([msg, chatbot]) # clear chat history
    msg.submit(get_intent, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch() # launch web app
