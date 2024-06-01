import websockets, asyncio, librosa, os, librosa, json
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import keras.utils as image
import soundfile as sf
from tensorflow.keras.applications.mobilenet import preprocess_input
from tensorflow.keras.applications import MobileNetV2


# with tf.device('/CPU:0'):
try:
    async def process_audio(websocket):
        di={}
        wave_bytes = await websocket.recv()
        print('\ndata recieved!')
        audio_data = np.frombuffer(wave_bytes, dtype=np.float32)
        sf.write('temp/t.wav', audio_data, sample_rate)

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

        ms = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)
        log_ms = librosa.power_to_db(ms, ref=np.max)
        librosa.display.specshow(log_ms, sr=sample_rate)

        canvas = fig.canvas
        canvas.draw()
        width, height = canvas.get_width_height()
        image_array = np.frombuffer(canvas.tostring_rgb(), dtype='uint8')
        image_array = image_array.reshape(height, width, 3)
        images = tf.image.resize(image_array, (224,224)) 

        x = np.expand_dims(images, axis=0)
        x = preprocess_input(np.array(x))
        y = base_model.predict(x, verbose=False)
        predicted_probs = model.predict(y, verbose=False)

        prediction_percentages=predicted_probs[0] * 100
        for i, c in enumerate(class_labels):
            di[c]=round(float(prediction_percentages[i]), 2)

        j_dic = json.dumps(di)
        await websocket.send(j_dic)
        print("Prediction sent!")

except Exception as e:
    print(e)


async def main():
    async with websockets.serve(process_audio, "localhost", 8000):
        print()
        print("WebSocket server is running on ws://localhost:8000")
        await asyncio.Future()


if __name__ == "__main__":
    if not os.path.exists('temp'):
        os.makedirs('temp')

    sample_rate=8000
    class_labels=['IVR', 'Music', 'Speech']
    model_name='ann_mobilenetv2_1_sec.h5'
    model = tf.keras.models.load_model(model_name)
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    asyncio.run(main())
