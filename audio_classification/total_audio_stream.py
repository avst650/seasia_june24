import matplotlib.pyplot as plt
import os, tempfile, librosa, pyaudio
import numpy as np
from sklearn.preprocessing import LabelEncoder
# from datetime import datetime
from keras.models import load_model
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
import datetime
from datetime import datetime
import random
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import soundfile as sf
import concurrent.futures
from threading import Thread
from streamlit.runtime.scriptrunner import add_script_run_ctx
import tensorflow as tf
import pathlib
from scipy import signal
import keras.utils as image
from pydub import AudioSegment
from tensorflow.keras.applications.mobilenet import preprocess_input
from tensorflow.keras.applications import MobileNetV2, VGG19
import soundfile as sf
import sounddevice as sd
import time

with tf.device('/CPU:0'):
    # @st.cache(suppress_st_warning=True)
    def process_audio(aud_data):

        sd.play(aud_data, RATE)
        sd.wait()
        print(aud_data,'thirdd')
        #
        # plt.figure(figsize=(14, 5))
        # librosa.display.waveshow(aud_data, sr=8000)
        # plt.savefig('save_image/after_processing.png')

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

        ms = librosa.feature.melspectrogram(y=aud_data, sr=8000)
        log_ms = librosa.power_to_db(ms, ref=np.max)
        librosa.display.specshow(log_ms, sr=RATE)
        fig.savefig(f'temp/temp.png')

        images = image.img_to_array(image.load_img('temp/temp.png', target_size=(224, 224)))
        os.remove('temp/temp.png')

        x = np.expand_dims(images, axis=0)
        x = preprocess_input(x)
        y = base_model.predict(x)
        predictions = model.predict(y)
        res = np.argmax(predictions, axis=1)
        # print(res,'nnnnnnnnnnnnnnnnnnnnnnnnnnnnn')
        # print(class_labels[res[0]],'hhhhhhhhhh')
        # lst.append(class_labels[res[0]])
        st.write('Predicted class: ' + class_labels[res[0]])
        # tee.write('Predicted class: ' + class_labels[res[0]])
        print('after rem')
        return None, pyaudio.paContinue

        # fig.close(all)
        # return None, pyaudio.paContinue

    def process_uploaded_audio():
        global tee
        global lst
        lst =[]
        tee = st.empty()
        audio_data, sr = librosa.load(f'temp/temp-{aaa}.wav',sr=8000)

        plt.figure(figsize=(14, 5))
        librosa.display.waveshow(audio_data, sr=8000)
        plt.savefig('save_image/after_load.png')

        print(audio_data,'second_array')
        os.remove(f'temp/temp-{aaa}.wav')

        r =RATE * 1
        while True:
            print(len(audio_data),'len_audio')
            if len(audio_data)>r:
                audio_data1 = audio_data[:r]
                audio_data =audio_data[r:]
                process_audio(audio_data1)
            else:
                print('yyyyyyyyyyyy')
                process_audio(audio_data)
                break


    if __name__ == '__main__':
        RATE = 8000
        FORMAT = pyaudio.paFloat32
        CHANNELS = 1
        audio_interface = pyaudio.PyAudio()
        base_dir = pathlib.Path(__name__).parent.absolute()
        OUTPUT_DIR = base_dir
        class_labels = ['IVR', 'Music', 'Speech']

        aaa = random.random()
        model = tf.keras.models.load_model('mob_voice_1sec.h5')
        base_model = MobileNetV2(include_top=False, weights="imagenet", input_shape=(224, 224, 3))

        if not os.path.exists(os.path.join(OUTPUT_DIR, 'temp')):
            os.mkdir(os.path.join(OUTPUT_DIR, 'temp'))
        st.title('Audio Classifier')
        st.write('### Choose a sound file in .wav format')
        uploaded_file = st.file_uploader('Upload Audio', type=['wav', 'mp3'])
        if uploaded_file is not None:
            aud_byt=uploaded_file.read()
            # st.write('### Play audio')
            # st.audio(aud_byt)

            with open(os.path.join('temp', f'temp-{aaa}.wav'), 'wb') as a:
                a.write(aud_byt)
                a.seek(0)
            process_uploaded_audio()
