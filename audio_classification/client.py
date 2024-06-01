import asyncio, websockets, pyaudio, json, io, wave
import tensorflow as tf


def create_wav_buffer(raw_audio_buffer, sample_rate, bit_depth, num_channels):
    wav_buffer = io.BytesIO()

    # Create a WAV file writer in memory
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(bit_depth // 8)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(raw_audio_buffer)

    wav_buffer.seek(0)
    return wav_buffer


async def send_data():
    try:
        audio_stream = audio_interface.open(format=pyaudio.paFloat32,
                channels=num_channels,
                rate=sample_rate,
                input=True,
                frames_per_buffer=int(sample_rate * time_chunk))

        while True:
            async with websockets.connect("ws://localhost:8000") as websocket:
                    raw_data = audio_stream.read(int(sample_rate * time_chunk))
                    wav_buffer = create_wav_buffer(raw_data, sample_rate, bit_depth, num_channels)

                    wb=wave.open(wav_buffer)
                    samples = wb.getnframes()
                    wav_bytes = wb.readframes(samples)

                    await websocket.send(wav_bytes)
                    print('\ndata sent!')

                    prediction = await websocket.recv()
                    j_pred=json.loads(prediction)
                    print(f"The predicted recieved: {j_pred}")

    except websockets.exceptions.ConnectionClosed as e:
        print()
        print(e)
        audio_stream.stop_stream()
        audio_stream.close()
        audio_interface.terminate()
        print("WebSocket connection closed!")


if __name__ == "__main__":

    audio_interface = pyaudio.PyAudio()
    sample_rate = 8000
    bit_depth = 32
    num_channels = 1
    time_chunk=1

    asyncio.run(send_data())


# audio=np.frombuffer(stream.read(CHUNK),dtype=np.int16)
# S = librosa.feature.melspectrogram(audio.astype('float32'), sr=RATE)