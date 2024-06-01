
# import asyncio
# import cv2
# from mtcnn import MTCNN

# async def detect_faces(frame, detector):
#     faces = detector.detect_faces(frame)
#     return faces

# async def main():
#     video_capture = cv2.VideoCapture("/dev/video2")

#     if not video_capture.isOpened():
#         print("Error: Webcam not found.")
#         return

#     detector = MTCNN()

#     while True:
#         ret, frame = video_capture.read()

#         if not ret:
#             break

#         # Asynchronously detect faces
#         future = asyncio.ensure_future(detect_faces(frame, detector))

#         # Continue with other processing while waiting for face detection
#         # Example: You can display the original frame, do other image processing, etc.

#         # Simulate other processing (Replace this with your actual processing)
#         await asyncio.sleep(0.02)  # Sleep for 20ms (approx. 50 FPS)

#         # Now, when you actually need the face detection results, await the future
#         faces = await future

#         # Draw rectangles around the detected faces
#         for face in faces:
#             x, y, w, h = face['box']
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

#         # Display the frame with detected faces
#         cv2.imshow('Face Detection', frame)

#         # Exit the loop when 'q' key is pressed
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # Release the video capture and close the window
#     video_capture.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     asyncio.run(main())



import cv2
import queue
import threading

# Function to read frames from video and put them in the queue
def read_frames_to_queue(video_path, queue, max_frames=None):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        queue.put(frame)

        frame_count += 1
        if max_frames is not None and frame_count >= max_frames:
            break

    cap.release()

# Example usage:
# Create a queue to store frames
frame_queue = queue.Queue()

# Define the video path
video_path = 0
# Start the frame reading thread
frame_reader_thread = threading.Thread(target=read_frames_to_queue, args=(video_path, frame_queue,))

# Start reading frames from the video and putting them in the queue
frame_reader_thread.start()

# ... Your face recognition threads can now process frames from the queue ...
# Make sure you have 15 threads (or the desired number) processing the frames simultaneously.

# Wait for the frame reading thread to finish (optional)
frame_reader_thread.join()

# After all processing is done, you can clean up the queue
frame_queue.queue.clear()
