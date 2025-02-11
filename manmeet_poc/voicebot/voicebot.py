import os
import streamlit as st
import speech_recognition as sr
import google.generativeai as genai
from gtts import gTTS
import pygame
import io
from dotenv import load_dotenv

class VoiceBot:
    def __init__(self):
        load_dotenv()
        # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key="AIzaSyD46sQnDyv2IWmJEOx4TF8jmZV-L3038PE")
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        self.recognizer = sr.Recognizer()
        self.gemini_model = genai.GenerativeModel("gemini-pro")
        self.voices = {
            "Aria": "9BWtsMINqrJLrRacOk9x",
            "Roger": "CwhRBWXzGAHq8TQ4Fs17",
            "Sarah": "EXAVITQu4vr4xnSDxMaL",
        }
        self.current_voice = "Aria"
        self.current_model = "eleven_multilingual_v2"

    def text_to_speech(self, text, language='en'):
        """
        Convert text to speech using gTTS and play the audio.
        
        Args:
            text (str): Text to convert to speech
            language (str, optional): Language code. Defaults to 'en'.
        """
        try:
            # Create a gTTS object
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to a byte buffer instead of a file
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            # Load the audio from the byte buffer
            pygame.mixer.music.load(fp)
            
            # Play the audio
            pygame.mixer.music.play()
            
            # Wait for the audio to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        
        except Exception as e:
            st.error(f"Text-to-speech error: {e}")
    
    def speech_to_text(self):
        """
        Capture speech and convert to text with improved noise handling.
        
        Returns:
            str: Transcribed text or None if recognition fails
        """
        with sr.Microphone() as source:
            st.info("Listening... Speak clearly.")
            
            # Dynamic noise adjustment
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.recognizer.pause_threshold = 1.5  # Tolerate short pauses

            try:
                # Listen for speech
                audio = self.recognizer.listen(source, timeout=11, phrase_time_limit=11)
                
                # Recognize speech using Google API
                text = self.recognizer.recognize_google(audio)
                    
                return text
            except sr.UnknownValueError:
                st.warning("I couldn't understand. Please try again.")
                return None
            except sr.RequestError as e:
                st.error(f"STT service error: {e}")
                return None
            except sr.WaitTimeoutError:
                st.info("Listening timeout reached. Try speaking again.")
                return None

    def generate_response(self, user_input):
        """
        Generate a response using Gemini Pro, strictly based on the provided data.
        """
        # Directly use the user's input for response generation
        data_context = """
        Here is the available data for reference:
        - Emission of Texas region: 37898 tons
        - Highest emission carrier in 2024: BUNGE OILS - WAINWRIGHT AB
        - Emissions intensity for Region san fransisco in June 2023: 467777 gCO2e/Ton-Mile
        - Total shipments for modesto: 6783
        - Emission intensity for Region Midwest: 467777 gCO2e/Ton-Mile
        - Total emissions for the lane from Tacoma,to Lancaster: 11,802.84 tons
        - Total shipments for the lane from Tacoma to Lancaster: 2,484
        - Emission intensity for the lane from Tacoma to Lancaster: 256.13 tons per ton-mile
        - Total emissions from CHARLOTTE to ABERDEEN: 788883 tons
        - Total emission of carrier Carl Vinson: 0.718 tCO2e
        - Total emission of carrier Nimitz: 0.745 tCO2e
        """
        
        # Prompt strictly requesting responses from data
        prompt = (
            f"This assistant is named G-Sight. G-Sight must respond to user queries strictly based on the following data:\n{data_context}\n"
            f"If the user greets, respond appropriately in a sentence. Otherwise, provide answers strictly related to the given data context.\n"
            f"User Input: {user_input}\n"
            f"G-Sight's Response:"
        )

        
        try:
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            return response_text
        except Exception as e:
            st.error(f"Error generating response: {e}")
            return "I'm having trouble processing that right now."

def main():
    st.title("🎙️ Gemini Voice Bot")

    if "voice_bot" not in st.session_state:
        st.session_state.voice_bot = VoiceBot()

    if "stop_listening" not in st.session_state:
        st.session_state.stop_listening = False

    # st.sidebar.header("Voice Settings")
    # selected_voice = st.sidebar.selectbox("Choose Voice", list(st.session_state.voice_bot.voices.keys()), index=0)
    # st.session_state.voice_bot.current_voice = selected_voice

    # selected_model = st.sidebar.selectbox(
    #     "Choose Model",
    #     ["eleven_multilingual_v2", "eleven_multilingual_v1", "eleven_turbo_v2"],
    #     index=0,
    # )
    # st.session_state.voice_bot.current_model = selected_model

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎤 Speak"):
            # Reset stop listening flag
            st.session_state.stop_listening = False
            
            # Capture speech
            user_input = st.session_state.voice_bot.speech_to_text()
            
            if user_input:
                st.text(f"User: {user_input}")
                
                # Generate response
                response = st.session_state.voice_bot.generate_response(user_input)
                st.text(f"Bot: {response}")
                
                # Text to speech
                st.session_state.voice_bot.text_to_speech(response)

    with col2:
        if st.button("🛑 Stop"):
            st.session_state.stop_listening = True
            # Stop the TTS playback
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            st.info("Microphone and playback stopped.")

if __name__ == "__main__":
    main()
