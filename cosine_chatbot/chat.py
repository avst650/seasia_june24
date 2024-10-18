import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

def preprocess_text(text):
    words = nltk.word_tokenize(text)
    words = [word.lower() for word in words]
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]
    processed_text = ' '.join(words)
    return processed_text

def get_intent(user_input):
    preprocessed_input = preprocess_text(user_input)
    user_vector = tfidf_vectorizer.transform([preprocessed_input])
    similarities = cosine_similarity(user_vector, tfidf_matrix)
    max_similarity = similarities.max()
    
    if max_similarity < 0.4:
        intent = ''
        response = 'sorry, nothing found!'
    else:
        intent_index = similarities.argmax() 
        response = data['file'][intent_index]

    return response


data = pd.read_csv('num.csv')
nltk.download('stopwords')
nltk.download('punkt')
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(data['user'])

inp=input("Enter query: ")
response=get_intent(inp)
print(response)