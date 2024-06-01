from ultralytics import YOLO
import cv2
from ultralytics.utils.plotting import Annotator
import pickle 
from sklearn.preprocessing import Normalizer
import multiprocessing
from architecture import InceptionResNetV2
from scipy.spatial.distance import cosine
import numpy as np
import tensorflow as tf
import pytz, os, cv2, pyttsx3, time, shutil, base64, json, threading, mtcnn, pickle, decimal




# def load_pickle(path):
#     with open(path, 'rb') as f:
#         encoding_dict = pickle.load(f)
#     return encoding_dict


# def normalize(img):
#     mean, std = img.mean(), img.std()
#     return (img - mean) / std



# encodings_path = 'encodings/encodings.pkl'
# encoding_dict = load_pickle(encodings_path)
# recognition_t = 0.3
# l2_normalizer = Normalizer('l2')
# required_shape = (160, 160)
# def face_recognition_process(queue):
#         face_encoder = InceptionResNetV2()
#         face_encoder.load_weights("facenet_keras_weights.h5")
#         status = "IN"
#         while True:
#             if not queue.empty():
#                 arr=queue.get()
#                 face_img = arr[0]
#                 img_time= arr[3]
#                 face_normalized = normalize(face_img)
#                 face_resized = cv2.resize(face_normalized, required_shape)
#                 face_d = np.expand_dims(face_resized, axis=0)
#                 encode= face_encoder.predict(face_d, verbose=False)
#                 encode = np.sum(encode, axis=0)
#                 encode = np.expand_dims(encode, axis=0)
#                 encode = l2_normalizer.transform(encode.reshape(1, -1))[0]
#                 min_distance = float('inf')
#                 id1 = '1' 
#                 for db_name, db_encode in encoding_dict.items():
#                     dist = cosine(db_encode, encode)
#                     if dist < recognition_t and dist < min_distance:
#                         id1 = db_name
#                         min_distance = dist
#                         print(min_distance)

#                 if 0.950 <= arr[1] <= 1:
#                     # if registration.objects.filter(id=id1).exists():
#                     reg_obj = registration.objects.get(id=id1)
#                     r = attendance.objects.filter(emp_id=reg_obj).order_by('-date_time').first()
#                     if r == None:
#                         retv, buffer1 = cv2.imencode('.jpg', arr[2])
#                         emp_img_string1 = buffer1.tobytes()
#                         attendance.objects.create(emp_id=reg_obj,status=status,image=emp_img_string1, date_time=img_time)
                    
#                     elif id1!='1':
#                         prev_status=r.status
#                         prev_date= r.date_time
#                         if prev_status!=status or datetime.now().astimezone().date()!=prev_date.date():
#                             retv, buffer1=cv2.imencode('.jpg', arr[2])
#                             emp_img_string1=buffer1.tobytes()
#                             attendance.objects.create(emp_id=reg_obj,status=status,image=emp_img_string1,date_time=img_time)
                    
#                     elif id1=='1':
#                         u= unknown.objects.filter().order_by('-date_time').first()
#                         if u == None:
#                             retv, buffer2=cv2.imencode('.jpg', arr[2])
#                             emp_img_string1 = buffer2.tobytes()
#                             unknown.objects.create(status=status,image=emp_img_string1,date_time=img_time)
#                         else:
#                             prev_status=u.status
#                             prev_time=u.date_time
#                             now_time=datetime.now().astimezone()
#                             sec=now_time-prev_time
#                             seconds=sec.total_seconds()
#                             if prev_status!=status or seconds > 20:
#                                 retv, buffer1=cv2.imencode('.jpg', arr[2])
#                                 emp_img_string1 = buffer1.tobytes()
#                                 unknown.objects.create(status=status,image=emp_img_string1,date_time=img_time)
#                     # else:
#                     #     print("User Not found in database")
#                 else:
#                     if id1=='1':
#                         u= unknown.objects.filter().order_by('-date_time').first()
#                         if u == None:
#                             retv, buffer2=cv2.imencode('.jpg', arr[2])
#                             emp_img_string1 = buffer2.tobytes()
#                             unknown.objects.create(status=status,image=emp_img_string1,date_time=dt_string1)
#                             print("first Unknown Person deteced with low confidence rate at the IN camera")
                    
#                         else:
#                             prev_status=u.status
#                             prev_time=u.date_time
#                             now_time=datetime.now().astimezone()
#                             sec=now_time-prev_time
#                             seconds=sec.total_seconds()
#                             if prev_status!=status or seconds > 20:
#                                 retv, buffer1=cv2.imencode('.jpg', arr[2])
#                                 emp_img_string1 = buffer1.tobytes()
#                                 unknown.objects.create(status=status,image=emp_img_string1,date_time=dt_string1)                    
#                     else:
#                         pass



# Load YOLO models
person_model = YOLO('yolov8n.pt')
face_model = YOLO('yolov8n-face.pt')
line_thickness = 1
edge_thickness=1
# Capture video
cap = cv2.VideoCapture("rtsp://admin:admin123@10.8.21.47:554/cam/realmonitor?channel=1&subtype=0")
# cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('/dev/video0')
face_detector = cv2.FaceDetectorYN.create("yunet_22mar.onnx", "", (160, 160))
# queue = multiprocessing.Queue()
# recognition_process = multiprocessing.Process(target=face_recognition_process, args=(queue,))
# recognition_process.start()
frame_count = 1
while True:

    _, img = cap.read()

    if frame_count == 31:
        print("?????????????????????")
        frame_count = 1
        
    print(frame_count)                       


    if frame_count % 5 == 0:
        print("processed: ", frame_count)
        person_results = person_model.predict(img, verbose=False)
        for r in person_results:
            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0]
                c = box.cls
                if int(c) == 0:
                    x01, y01, x02, y02 = [int(i) for i in b]
                    cv2.rectangle(img, (x01, y01), (x02, y02), (0, 255, 0), line_thickness)
                    person_img = img[y01:y02, x01:x02]  # Crop the person's region
                    img_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    height, width, _ = img_RGB.shape
                    face_detector.setInputSize((width, height))
                    _, faces = face_detector.detect(img_RGB)
                    if faces is not None:
                        for face in faces:
                            face_confidence = float(face[-1])
                            confidence = decimal.Decimal(face_confidence).quantize(decimal.Decimal('0.0001'), rounding=decimal.ROUND_DOWN)
                            x1, y1, w, h = list(map(int, face[:4]))
                            x1, y1 = abs(x1), abs(y1)
                            x2, y2 = x1 + w, y1 + h
                            face_img = img_RGB[y1:y2, x1:x2]
                            # dat1 = timezone.now()
                            # dt_string1 = dat1.strftime("%Y-%m-%d %H:%M:%S:%f")
                            # ar=(face_img, confidence, img,dt_string1)
                            # queue.put(ar)

                            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), line_thickness)
                            cv2.putText(img, f"{w}, {h}" , (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                            cv2.line(img, (x1, y1), (x1 + int(w/4), y1), (0, 255, 255), edge_thickness)
                            cv2.line(img, (x1, y1), (x1, y1 + int(h/4)), (0, 255, 0), edge_thickness)
                            cv2.line(img, (x1 + int(3*w/4), y1), (x2, y1), (0, 255, 0), edge_thickness)
                            cv2.line(img, (x2, y1 + int(h/4)), (x2, y1), (0, 255, 255), edge_thickness)
                            cv2.line(img, (x1, y1 + int(3*h/4)), (x1, y2), (0, 255, 255), edge_thickness)
                            cv2.line(img, (x1 + int(w/4), y2), (x1, y2), (0, 255, 0), edge_thickness)
                            cv2.line(img, (x1 + int(3*w/4), y2), (x2, y2), (0, 255, 255), edge_thickness)
                            cv2.line(img, (x2, y2 - int(h/4)), (x2, y2), (0, 255, 0), edge_thickness)
                        
                        
                    else:
                        print("unknown person detected")

    frame_count += 1
               
     
    cv2.imshow('YOLO V8 Detection (Persons & Faces)', img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
