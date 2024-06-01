import asyncio, websockets, pyaudio, json, io, wave
import tensorflow as tf

async def send_data():
    try:
        audio_stream = audio_interface.open(format=pyaudio.paFloat32,
                channels=num_channels,
                rate=sample_rate,
                input=True,
                frames_per_buffer=int(sample_rate * time_chunk))

        while True:
            async with websockets.connect("ws://localhost:8000") as websocket:
                    raw_data = audio_stream.read(sample_rate * time_chunk)
                    await websocket.send(raw_data)
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
