import sounddevice as sd
import speech_recognition as sr
import numpy as np
import io
import wave
import requests
import time

def query(audio_data):
    response = requests.post(API_URL, headers=headers, data=audio_data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"API Error: {response.status_code}, {response.text}")
        return None

# Hugging Face Whisper API configuration
API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo"
headers = {"Authorization": "Bearer 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"}

recognizer = sr.Recognizer()

with sr.Microphone() as source:    
    # Dynamic noise adjustment
    recognizer.adjust_for_ambient_noise(source, duration=1)
    recognizer.pause_threshold = 1.5  # Tolerate short pauses

    # Listen for speech
    print("Listening... Speak clearly.")
    audio = recognizer.listen(source, timeout=11, phrase_time_limit=11)

# # print(type(audio.AudioData))
#     text = recognizer.recognize_google(audio, language='en-IN')
#     print (text)
    
print ("Processing...")

audio_wav=audio.get_wav_data()

response = query(audio_wav)

if response and "text" in response:
    text = response["text"]
    print(f"Transcription: {text}")
else:
    print("Could not transcribe audio. Try again.")
