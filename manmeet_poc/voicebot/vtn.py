import os
import streamlit as st
import asyncio
import speech_recognition as sr
import google.generativeai as genai
from gtts import gTTS
import pygame
import io
from dotenv import load_dotenv
import time
 
class VoiceBot:
    def __init__(self):
        load_dotenv()
        GOOGLE_API_KEY ="AIzaSyD46sQnDyv2IWmJEOx4TF8jmZV-L3038PE"
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        self.recognizer = sr.Recognizer()
        self.gemini_model = genai.GenerativeModel("gemini-pro")
        self.conversation_history = []
        self.voices = {
            "Aria": "9BWtsMINqrJLrRacOk9x",
            "Roger": "CwhRBWXzGAHq8TQ4Fs17",
            "Sarah": "EXAVITQu4vr4xnSDxMaL",
        }
        self.current_voice = "Aria"
        self.current_model = "eleven_multilingual_v2"
 
    async def stream_speech_to_text(self):
        """Stream speech to text asynchronously, listening in 3-second chunks until the user stops."""
        with sr.Microphone() as source:
            st.info("Listening... Speak now.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.recognizer.non_speaking_duration = 1
            self.recognizer.pause_threshold = 1 # Adjust for natural pauses
            
            while True:
                if st.session_state.stop_listening:
                    st.info("Stopped listening.")
                    break
                
                # Listen in chunks of 3 seconds
                start_time = time.time()
                try:
                    # Capture audio for 3 seconds
                    audio = self.recognizer.listen(source, timeout=1)
                    elapsed_time = time.time() - start_time
 
                    if elapsed_time >= 0.1:  # Ensure it listens for 3 seconds (or less if silence)
 
                        text = self.recognizer.recognize_google(audio)
                        yield text
                    else:
                        # If there's still time remaining, wait before capturing the next chunk
                        time.sleep(0.1 - elapsed_time)
                except Exception:
                    # st.warning("I didn't catch that. Could you repeat?")
                    continue
 
 
    def generate_response(self, user_input):
        """Generate response using Gemini Pro."""
        self.conversation_history.append(f"User: {user_input}")
        context = "\n".join(self.conversation_history[-5:])
        prompt = f"Continue this conversation in short based on the context. Provide responses in 2-5 lines without punctuation or special characters:\n{context}\n\nNext response:"
        try:
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            self.conversation_history.append(f"{response_text}")
            return response_text
        except Exception as e:
            st.error(f"Error generating response: {e}")
            return "I'm having trouble processing that right now."
 
 
 
async def main():
    st.title("🎙️ Voice Notes")
    
    if "voice_bot" not in st.session_state:
        st.session_state.voice_bot = VoiceBot()
 
    if "stop_listening" not in st.session_state:
        st.session_state.stop_listening = False
        
    output_placeholder = st.empty()
    
    if "conversation_output" not in st.session_state:
        st.session_state.conversation_output = ""
 
    # Layout: Speak button, conversation output, Stop button
    speak_button_col, = st.columns([1])  # Create one column for the Speak button
    
    with speak_button_col:
        if st.button("🎤 Speak"):
            st.session_state.stop_listening = False
            # Stream speech-to-text and update conversation output
            async for chunk in st.session_state.voice_bot.stream_speech_to_text():
                if chunk:
                    st.session_state.conversation_output += f"{chunk} "
                    output_placeholder.text(st.session_state.conversation_output)  # Display updated conversation
                if st.session_state.stop_listening:
                    break
 
    # Display the conversation output below the Speak button
    st.text_area("Conversation Output", value=st.session_state.conversation_output, height=150)
 
    # Now, create another button under the conversation output to stop listening
    stop_button_col, = st.columns([1])  # Create one column for the Stop button
 
    with stop_button_col:
        if st.button("🛑 Stop"):
            st.session_state.stop_listening = True
            # Stop the TTS playback if active
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            # st.info(st.session_state.conversation_output)  # Display final conversation output when stopped
 
if __name__ == "__main__":
    asyncio.run(main())