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
from collections import Counter
import time

with tf.device('/CPU:0'):
    def process_audio(aud_data, c):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

        ms = librosa.feature.melspectrogram(y=aud_data.astype('float32'), sr=8000)
        log_ms = librosa.power_to_db(ms, ref=np.max)
        librosa.display.specshow(log_ms, sr=8000)

        canvas = fig.canvas
        canvas.draw()
        width, height = canvas.get_width_height()
        image_array = np.frombuffer(canvas.tostring_rgb(), dtype='uint8')
        image_array = image_array.reshape(height, width, 3)
        images = tf.image.resize(image_array, (224,224)) 

        x = np.expand_dims(images, axis=0)
        x = preprocess_input(np.array(x))
        y = base_model.predict(x, verbose=False)
        predictions = model.predict(y, verbose=False)
        res = np.argmax(predictions, axis=1)
        st.write(f'Predicted class {c}: ' + class_labels[res[0]])
        lst.append(class_labels[res[0]])

        # fig.closeAll()
        return None, pyaudio.paContinue

    def process_uploaded_audio(c, aud_data):
        global tee
        global lst
        lst =[]
        tee = st.empty()
        audio_data=aud_data

        # plt.figure(figsize=(14, 5))
        # librosa.display.waveshow(audio_data.astype('float32'), sr=8000)
        # plt.savefig('save_image/after_load.png')

        r =RATE * 1
        while True:
            c+=1
            if len(audio_data)>r:
                audio_data1 = audio_data[:r]
                audio_data =audio_data[r:]
                process_audio(audio_data1, c)
            else:
                process_audio(audio_data, c)
                break


    if __name__ == '__main__':
        RATE = 8000
        FORMAT = pyaudio.paFloat32
        CHANNELS = 1
        audio_interface = pyaudio.PyAudio()
        base_dir = pathlib.Path(__name__).parent.absolute()
        OUTPUT_DIR = base_dir
        class_labels = ['IVR', 'Music', 'Silence', 'Speech']
        global ls
        global c
        c=0

        ls=[]

        aaa = random.random()
        model = tf.keras.models.load_model('ann_mobilenetv2_1s_4.h5')
        base_model = MobileNetV2(include_top=False, weights="imagenet", input_shape=(224, 224, 3))

        if not os.path.exists(os.path.join(OUTPUT_DIR, 'temp')):
            os.mkdir(os.path.join(OUTPUT_DIR, 'temp'))
            
        st.title('Audio Classifier')
        st.write('### Choose a sound file in .wav format')
        uploaded_file = st.file_uploader('Upload Audio', type=['wav', 'mp3', 'raw'])
        if uploaded_file is not None:
            aud_byt=uploaded_file.read()
            audio_data = np.frombuffer(aud_byt, dtype=np.int16)
            print(len(audio_data))
            
            process_uploaded_audio(c, audio_data)


            def count_unique_elements(lst):
                return Counter(lst)

            result = count_unique_elements(lst)
            for item, count in result.items():
                st.write(f"{item}: {count}")
