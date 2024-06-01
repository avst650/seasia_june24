from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from apps.home.models import *
from datetime import datetime, timedelta ,date
from django.http import HttpResponseNotFound
from django.db.models import Count, Min, Max, Q, Value
from django.db.models.functions import Coalesce
from .models import registration, attendance
from django.views.decorators import gzip
from django.shortcuts import render
from datetime import datetime, timezone
from apps.home.architecture import *
from sklearn.preprocessing import Normalizer
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import mediapipe as mp
import pytz, os, cv2, pyttsx3, time, shutil, base64, json, threading, mtcnn, pickle, decimal
from calendar import monthrange
from django.core.exceptions import ObjectDoesNotExist
import numpy as np
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import tensorflow as tf
import multiprocessing
from keras.models import load_model
from scipy.spatial.distance import cosine
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from apps.home.form import AttendanceForm
from django.core.paginator import Paginator, EmptyPage
from pytz import timezone as tz
from ultralytics import YOLO
import cv2
from ultralytics.utils.plotting import Annotator


global dic
dic={
    'id':None,
    'name':None,
    'department':None,
    'img_string':None
}



def load_pickle(path):
    with open(path, 'rb') as f:
        encoding_dict = pickle.load(f)
    return encoding_dict


def normalize(img):
    mean, std = img.mean(), img.std()
    return (img - mean) / std


@login_required(login_url="/login/")
def index(request):
    return render(request,"home/index.html")


@login_required(login_url="/login/")
def user_register(request):
    ignored_id = 1
    employees = registration.objects.all().order_by('-id').exclude(id=ignored_id)

    paginator = Paginator(employees, 10)  # You can adjust the page size as needed
    page_num = request.GET.get('page')

    try:
        paginated_data = paginator.get_page(page_num)
    except EmptyPage:
        # Handle the case where the requested page is out of range
        paginated_data = paginator.get_page(1)

    context = {'data': []}
    for item in paginated_data:
        image_data = item.image  
        image_data_base64 = base64.b64encode(image_data).decode('utf-8')
        context['data'].append({'item': item, 'image_data_base64': image_data_base64})

    context['paginated_data'] = paginated_data  # Add paginated_data to context for pagination links
    return render(request, "home/user_registration.html", context)


def user_register_attendance(request, id):
    uid = int(id)
    current_date = datetime.now().strftime('%Y-%m-%d')
    user_attendance = attendance.objects.filter(emp_id=uid, date_time__contains=current_date)
    context = {'data': []}
    if user_attendance.exists():
        status ="Present"
        for item in user_attendance:
            image_data = item.image 
            image_data_base64 = base64.b64encode(image_data).decode('utf-8')
            context['data'].append({'item': item, 'image_data_base64': image_data_base64, "status":status })
    else:
        user_data=registration.objects.get(id=uid)
        image_data_base64 = base64.b64encode(user_data.image).decode('utf-8')
        context = {'data': []}
        status="Absent"
        context['data'].append({
            "item": user_data, "image_data_base64":image_data_base64, "status":status
        })
    return render(request, "home/user_registration_attendance.html", context)


def get_id(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id = data.get('inputid')
        name = data.get('inputname')
        dept = data.get('inputdepartment')
        dic['id'], dic['name'], dic['dept']=id, name, dept
        if dic['id'] == 'None':
            pass
        else: 
            print(dic['id'])
            print(dic['name'])
            print(dic['dept'])
    return JsonResponse({"status": "success"})


def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    
    
def speech_thread(text):
    thread = threading.Thread(target=text_to_speech, args=(text,))
    thread.start()
    
    
def capture_video():
    mp_face_detection = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh()
    # cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture('/dev/video0')
    # cap = cv2.VideoCapture('/dev/video2')
    # cap = cv2.VideoCapture("rtsp://admin:admin123@10.8.21.48:554/cam/realmonitor?channel=1&subtype=1")
    face_id = dic['id']
    face_position = "Center"
    output_directory = 'emp_dataset/dataset_color/'
    if os.path.isdir(output_directory):
            shutil.rmtree(output_directory)
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    frame1 = None
    image_count = 0
    capture_interval = 3 
    image_counts = {"Left": 0, "Right": 0, "Up": 0, "Down": 0, "Center": 0}
    
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        frame2 = frame.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(frame_rgb)
        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x, y, w, h = int(bbox.xmin * frame.shape[1]), int(bbox.ymin * frame.shape[0]), \
                            int(bbox.width * frame.shape[1]), int(bbox.height * frame.shape[0])
                x_offset = int(-0.1 * w) 
                y_offset = int(-0.2 * h)  
                x, y, w, h = x + x_offset, y + y_offset, w - 2 * x_offset, h - y_offset
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_landmarks = face_mesh.process(frame_rgb)
                if face_landmarks.multi_face_landmarks:
                    for face_landmark in face_landmarks.multi_face_landmarks:
                        nose_x = int(face_landmark.landmark[4].x * frame.shape[1])
                        nose_y = int(face_landmark.landmark[4].y * frame.shape[0])
                        if nose_x < x + 0.4 * w:
                            face_position = "Left"
                        elif nose_x > x + 0.6 * w:
                            face_position = "Right"
                        elif nose_y < y + 0.5 * h:
                            face_position = "Up"
                        elif nose_y > y + 0.6 * h:
                            face_position = "Down"
                        else:
                            face_position = "Center"
                        mp_drawing.draw_landmarks(frame, face_landmark, mp_face_mesh.FACEMESH_TESSELATION,
                                                landmark_drawing_spec=None,
                                                connection_drawing_spec=mp_drawing.DrawingSpec(
                                                    color=(255, 255, 255), thickness=1, circle_radius=1))
                else:
                    face_position = "Please show the face properly"
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, face_position, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        if frame1 is None:
            frame1 = frame.copy()
        if face_position != "Please show the face properly":
            image_counts[face_position] += 1
            if image_counts[face_position] <= 10:
                if frame1 is not None:
                    image_count += 1
                    image_filename = os.path.join(output_directory, f"image_{image_count}.jpg")
                    face_image = frame2[y:y+h, x:x+w]
                    face_image = cv2.resize(face_image, (160, 160))
                    cv2.imwrite(image_filename, frame2)
                    print(f"Saved image: {image_filename}")
                    if image_count==10:
                            img_str = cv2.imencode('.jpeg', frame2)[1].tostring()
                            dic['img_string'] = img_str
                            nparr = np.fromstring(img_str, np.uint8)
                            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                            cv2.imwrite(f'emp_{face_id}.jpeg', frame2)
                    frame1 = None
                    if image_counts[face_position] == 10:
                        additional_text = f"Captured 10 images for {face_position}"
                        cv2.putText(frame, additional_text, (frame.shape[1] - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                    (0, 0, 255), 2)
                        speech_thread(additional_text)
                        if image_count == 50:
                            time.sleep(3)
                            text = "all images captured thanks for your patience"
                            speech_thread(text)
                            time.sleep(3)
                            break
            else:
                pass
        ret, frame1 = cv2.imencode('.jpg', frame)
        response_bytes = (b'--frame1\r\n'
                        b'Content-Type: image/jpg\r\n\r\n' + frame1.tobytes() + b'\r\n')
        yield response_bytes
    cap.release()


@gzip.gzip_page
def camera_feed(request):
    try:  
        return StreamingHttpResponse(capture_video(), content_type="multipart/x-mixed-replace;boundary=frame")
    except Exception as e:
        print("An error occurred: ", e)
        return None
    

def train_data(request):
    if request.method == 'POST':
        uid = request.POST.get('myInput')
        uname=request.POST.get('intname')
        udept=request.POST.get('inputdept')
        user_img = dic['img_string']
        print(uid,uname,udept)
        id_exists=registration.objects.filter(id=uid).exists()
        if id_exists == False:
            if os.path.isdir('dataset'):
                shutil.rmtree("dataset")
            path=os.getcwd()
            os.chdir(f"{path}/emp_dataset")
            os.rename("dataset_color", f"{uid}")
            os.chdir(f"{path}")
            face_data ='emp_dataset/'
            required_shape = (160,160)
            face_encoder = InceptionResNetV2()
            path = "facenet_keras_weights.h5"
            face_encoder.load_weights(path)
            face_detector = mtcnn.MTCNN()
            encodes = []
            encoding_dict = dict()
            l2_normalizer = Normalizer('l2')
            for face_names in os.listdir(face_data):
                person_dir = os.path.join(face_data,face_names)
                for image_name in os.listdir(person_dir):
                    image_path = os.path.join(person_dir,image_name)
                    img_BGR = cv2.imread(image_path)
                    img_RGB = cv2.cvtColor(img_BGR, cv2.COLOR_BGR2RGB)
                    x = face_detector.detect_faces(img_RGB)
                    x1, y1, width, height = x[0]['box']
                    x1, y1 = abs(x1) , abs(y1)
                    x2, y2 = x1+width , y1+height
                    face = img_RGB[y1:y2 , x1:x2]
                    face = normalize(face)
                    face = cv2.resize(face, required_shape)
                    face_d = np.expand_dims(face, axis=0)
                    encode = face_encoder.predict(face_d)[0]
                    encodes.append(encode)
                if encodes:
                    encode = np.sum(encodes, axis=0 )
                    encode = l2_normalizer.transform(np.expand_dims(encode, axis=0))[0]
                    encoding_dict[face_names] = encode
            path = 'encodings/encodings.pkl'
            if os.path.exists(path):
                try:
                    with open(path, 'rb') as file:
                        existing_data = pickle.load(file)
                except (IOError, EOFError):
                    existing_data = {}
                existing_data.update(encoding_dict) 
                with open(path, 'wb') as file:
                    pickle.dump(existing_data, file)
            else:
                with open(path, 'wb') as file:
                    pickle.dump(encoding_dict, file)
            shutil.move(f"emp_dataset/{uid}", f"doneimagetraining/{uid}")
            dat = timezone.now()
            dat_str = dat.strftime("%Y-%m-%d %H:%M:%S:%f")
            registration.objects.create(id=uid, name=uname, department=udept, date_time=dat_str, image=user_img)
            data=registration.objects.get(id=uid)
            image_data = data.image
            context = {'imgdata': base64.b64encode(image_data).decode('utf-8')}
            dic['id']=None
            dic['name']=None
            dic['department']=None
            dic['img_string']=None
        else:
            print(id_exists," id allready exist ")
            return JsonResponse({"error":id_exists})
    return render(request,"home/after_index.html",{"data":data, "context":context})


def calculate_face_position(x_diff, y_diff):
    if abs(x_diff) < 30 and abs(y_diff) < 30:
        return "center"
    elif y_diff >= 30 and abs(x_diff) < y_diff:
        if x_diff >= 30:
            return "up-left"
        elif x_diff <= -30:
            return "up-right"
        else:
            return "up"
    elif y_diff <= -30 and abs(x_diff) < abs(y_diff):
        if x_diff >= 30:
            return "down-left"
        elif x_diff <= -30:
            return "down-right"
        else:
            return "down"
    elif x_diff >= 30 and abs(y_diff) < x_diff:
        return "left"
    elif x_diff <= -30 and abs(y_diff) < abs(x_diff):
        return "right"
    else:
        return "unknown"
    

def IN_Temp(request):
    return render(request,"home/INcam.html")   


def Out_Temp(request):
    return render(request,"home/OUTcam.html")


# def get_encode(face_encoder, face, size):
#     face = normalize(face)
#     face = cv2.resize(face, size)
#     encode = face_encoder.predict(np.expand_dims(face, axis=0), verbose=False)[0]
#     return encode


def create_one(request):
    id=1
    data=registration.objects.create(id=id, name='unknown', department='unknown', date_time=datetime.now(), image=None)
    data.save()
    return render (request, {"True"})


# def get_face(img, box):
#     x, y, w, h = box
#     x1, y1 = x, y
#     x2, y2 = x + w, y + h
#     face = img[y1:y2, x1:x2]
#     line_thickness = 1
#     edge_thickness = 5
#     cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), line_thickness)
#     cv2.line(img, (x1, y1), (x1 + int(w/4), y1), (0, 255, 255), edge_thickness)
#     cv2.line(img, (x1, y1), (x1, y1 + int(h/4)), (0, 255, 0), edge_thickness)
#     cv2.line(img, (x1 + int(3*w/4), y1), (x2, y1), (0, 255, 0), edge_thickness)
#     cv2.line(img, (x2, y1 + int(h/4)), (x2, y1), (0, 255, 255), edge_thickness)
#     cv2.line(img, (x1, y1 + int(3*h/4)), (x1, y2), (0, 255, 255), edge_thickness)
#     cv2.line(img, (x1 + int(w/4), y2), (x1, y2), (0, 255, 0), edge_thickness)
#     cv2.line(img, (x1 + int(3*w/4), y2), (x2, y2), (0, 255, 255), edge_thickness)
#     cv2.line(img, (x2, y2 - int(h/4)), (x2, y2), (0, 255, 0), edge_thickness)
#     return face, (x1, y1), (x2, y2)


# def detect(img, detector, encoder, encoding_dict):
#     img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     results = detector.detect_faces(img_rgb)
#     name = '0'
#     confidence = "unknown"
#     required_size = (160, 160)
#     recognition_t = 0.3

    
#     if len(results) == 0:  # No faces detected
#         return img, name, confidence
    
#     l2_normalizer = Normalizer('l2')
    
#     for res in results:
#         if res['confidence'] < confidence_t:
#             continue
#         face, pt_1, pt_2 = get_face(img, res['box']) 
#         encode = get_encode(encoder, face, required_size)
#         encode = l2_normalizer.transform(encode.reshape(1, -1))[0]
#         name = '1'
#         confidence = res
#         distance = float("inf")
#         for db_name, db_encode in encoding_dict.items():
#             dist = cosine(db_encode, encode)
#             print(dist)
#             if dist < recognition_t and dist < distance:
#                 print(dist,">>>>>>>>>>>>>>>>>>>>")
#                 name = db_name
#                 distance = dist
#         if name == '1':
#             cv2.rectangle(img, pt_1, pt_2, (0, 0, 255), 2)
#             cv2.putText(img, name, pt_1, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
#         else:
#             cv2.rectangle(img, pt_1, pt_2, (0, 255, 0), 2)
#             cv2.putText(img, name + f'__{distance:.2f}', (pt_1[0], pt_1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 1,
#                         (0, 200, 200), 2)
    
#     return img, name, confidence




























# def cam_in():
#     face_detector = cv2.FaceDetectorYN.create("yunet_22mar.onnx", "", (160, 160))
#     line_thickness = 1
#     edge_thickness=1
#     encodings_path = 'encodings/encodings.pkl'
#     encoding_dict = load_pickle(encodings_path)
#     recognition_t = 0.3
#     l2_normalizer = Normalizer('l2')
#     required_shape = (160, 160)
#     dat = timezone.now()
        
#     def face_recognition_process(queue):
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

#     queue = multiprocessing.Queue()
#     recognition_process = multiprocessing.Process(target=face_recognition_process, args=(queue,))
#     recognition_process.start()

#     # cap = cv2.VideoCapture("/dev/video2")
#     # cap = cv2.VideoCapture(0)
#     cap = cv2.VideoCapture("rtsp://admin:admin123@10.8.21.48:554/cam/realmonitor?channel=1&subtype=0")
#     while cap.isOpened():
#         ret, fram = cap.read()
#         if not ret:
#             print("Camera not opened")
#             break

#         frame=fram[225:1050, 420:1900]
#         # cv2.line(fram, (160, 120), (625, 120), (0, 255, 255), edge_thickness) #low resolution
#         cv2.rectangle(fram, (420, 225), (1900, 1050), (0, 255, 0), 2)  #high resolution 

#         img_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         height, width, _ = img_RGB.shape
#         face_detector.setInputSize((width, height))
#         _, faces = face_detector.detect(img_RGB)
#         if faces is not None:
#             for face in faces:
#                 face_confidence = float(face[-1])
#                 confidence = decimal.Decimal(face_confidence).quantize(decimal.Decimal('0.0001'), rounding=decimal.ROUND_DOWN)
#                 x1, y1, w, h = list(map(int, face[:4]))
#                 x1, y1 = abs(x1), abs(y1)
#                 x2, y2 = x1 + w, y1 + h
#                 face_img = img_RGB[y1:y2, x1:x2]
#                 dat1 = timezone.now()
#                 dt_string1 = dat1.strftime("%Y-%m-%d %H:%M:%S:%f")
#                 ar=(face_img, confidence, frame,dt_string1)
#                 queue.put(ar)

#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), line_thickness)
#                 cv2.putText(frame, f"{w}, {h}" , (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)

#                 cv2.line(frame, (x1, y1), (x1 + int(w/4), y1), (0, 255, 255), edge_thickness)
#                 cv2.line(frame, (x1, y1), (x1, y1 + int(h/4)), (0, 255, 0), edge_thickness)
#                 cv2.line(frame, (x1 + int(3*w/4), y1), (x2, y1), (0, 255, 0), edge_thickness)
#                 cv2.line(frame, (x2, y1 + int(h/4)), (x2, y1), (0, 255, 255), edge_thickness)
#                 cv2.line(frame, (x1, y1 + int(3*h/4)), (x1, y2), (0, 255, 255), edge_thickness)
#                 cv2.line(frame, (x1 + int(w/4), y2), (x1, y2), (0, 255, 0), edge_thickness)
#                 cv2.line(frame, (x1 + int(3*w/4), y2), (x2, y2), (0, 255, 255), edge_thickness)
#                 cv2.line(frame, (x2, y2 - int(h/4)), (x2, y2), (0, 255, 0), edge_thickness)

#         retd3, frame3 = cv2.imencode('.jpg', fram)
#         yield (b'--frame3\r\n'
#                 b'Content-Type: image/jpg\r\n\r\n' + frame3.tobytes() + b'\r\n')

#     recognition_process.join()
#     cap.release()


# @gzip.gzip_page
# def In_cam(request):
#     try:
#         return StreamingHttpResponse(cam_in(), content_type="multipart/x-mixed-replace;boundary=frame")
#     except Exception as e:
#         print("An error occurred: ", e)
#         return None


def get_encode(face_encoder, face, size):
    face = normalize(face)
    face = cv2.resize(face, size)
    encode = face_encoder.predict(np.expand_dims(face, axis=0), verbose=False)[0]
    return encode

# def detect(img, detector, encoder, encoding_dict):
#     img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     results = detector.detect_faces(img_rgb)
#     confidence_t=0.99
#     detected_ids = []
#     name = '0'
#     confidence = "unknown"
#     required_size = (160, 160)
#     recognition_t = 0.3
#     if len(results) == 0:  # No faces detected
#         detected_ids={
#             'id':name,
#             'distance':confidence
#         }
#         print(detected_ids)
#         return img, name, confidence
    
#     l2_normalizer = Normalizer('l2')
    
#     for res in results:
#         if res['confidence'] < confidence_t:
#             continue
#         face, pt_1, pt_2 = get_face(img, res['box'])
#         encode = get_encode(encoder, face, required_size)
#         encode = l2_normalizer.transform(encode.reshape(1, -1))[0]
#         name = '1'
#         confidence = res
#         cinfi=res['confidence']
#         distance = float("inf")
#         for db_name, db_encode in encoding_dict.items():
#             dist = cosine(db_encode, encode)
#             if dist < recognition_t and dist < distance:
#                 name = db_name
#                 distance = dist
#                 detected_ids.append({
#                                         'id':name,
#                                         'distance':cinfi
#                                         })
#         if name == '1':
#             print(name,">>>>>>>?????????????????????????")
#             cv2.rectangle(img, pt_1, pt_2, (0, 0, 255), 2)
#             cv2.putText(img, name, pt_1, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
#         else:
#             cv2.rectangle(img, pt_1, pt_2, (0, 255, 0), 2)
#             cv2.putText(img, name + f'__{distance:.2f}', (pt_1[0], pt_1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 1,
#                         (0, 200, 200), 2)
#     print(detected_ids)
#     return img, name, confidence

def get_face(img, box):
    x, y, w, h = box
    x1, y1 = x, y
    x2, y2 = x + w, y + h
    face = img[y1:y2, x1:x2]
    line_thickness = 1
    edge_thickness = 3
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), line_thickness)
    cv2.line(img, (x1, y1), (x1 + int(w/4), y1), (0, 255, 255), edge_thickness)
    cv2.line(img, (x1, y1), (x1, y1 + int(h/4)), (0, 255, 0), edge_thickness)
    cv2.line(img, (x1 + int(3*w/4), y1), (x2, y1), (0, 255, 0), edge_thickness)
    cv2.line(img, (x2, y1 + int(h/4)), (x2, y1), (0, 255, 255), edge_thickness)
    cv2.line(img, (x1, y1 + int(3*h/4)), (x1, y2), (0, 255, 255), edge_thickness)
    cv2.line(img, (x1 + int(w/4), y2), (x1, y2), (0, 255, 0), edge_thickness)
    cv2.line(img, (x1 + int(3*w/4), y2), (x2, y2), (0, 255, 255), edge_thickness)
    cv2.line(img, (x2, y2 - int(h/4)), (x2, y2), (0, 255, 0), edge_thickness)
    return face, (x1, y1), (x2, y2)


def detect(img, detector, encoder, encoding_dict):
    confidence_t = 0.99 
    recognition_t = 0.3
    l2_normalizer = Normalizer('l2')
    detected_ids = []
    name = '1'
    confidence = 'unknown'
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    results = detector.detect_faces(img_rgb )
    if not results:
        detected_ids.append({'id': name, 'confidence': confidence})
        return img, detected_ids

    for res in results:
        if res['confidence'] < confidence_t:
            continue

        face, pt_1, pt_2 = get_face(img, res['box'])
        encode = get_encode(encoder, face, (160, 160))
        encode = l2_normalizer.transform(encode.reshape(1, -1))[0]
        distance = float("inf")
        for db_name, db_encode in encoding_dict.items():
            dist = cosine(db_encode, encode)
            if dist < recognition_t and dist < distance:
                name = db_name
                distance = dist
        if name == '1':
            cv2.rectangle(img, pt_1, pt_2, (0, 0, 255), 2)
            cv2.putText(img, name, pt_1, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
            detected_ids.append({'id': name, 'confidence': res['confidence']})
        else:
            cv2.rectangle(img, pt_1, pt_2, (0, 255, 0), 2)
            cv2.putText(img, f'{name}__{distance:.2f}', (pt_1[0], pt_1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 200, 200), 2)
            detected_ids.append({'id': name, 'confidence': res['confidence']})
    return img, detected_ids










def face_recognition_process(queue):
    face_detector = mtcnn.MTCNN()
    path_m='facenet_keras_weights.h5'
    face_encoder= InceptionResNetV2()
    face_encoder.load_weights(path_m)
    encodings_path = 'encodings/encodings.pkl'
    encoding_dict = load_pickle(encodings_path)
    status = "IN"
    while True:
        if not queue.empty():
            arr=queue.get()
            frame0= arr['image']
            
            dt_string1=arr['time']
            frame , data = detect(frame0,face_detector,face_encoder,encoding_dict)
            if data :
                for i in data:
                    id1 = i['id']
                    print("********************",id1,"***************************")
                    confidence = i['confidence']
                    if id1 =='1'and confidence =='unknown':
                        pass
                        # u= unknown.objects.filter().order_by('-date_time').first()
                        # if u == None:
                        #     retv, buffer2=cv2.imencode('.jpg', frame)
                        #     emp_img_string1 = buffer2.tobytes()
                        #     unknown.objects.create(status=status,image=emp_img_string1,date_time=dt_string1)
                        # else:
                        #     prev_status=u.status
                        #     p_date=u.date_time
                        #     print(p_date,">>>>>>>>!!!!!!!!!!1111111111111!!!!!!!!>>>>>>>>>>>>>>>")
                        #     prev_time=p_date 
                        #     now_time = datetime.now().astimezone()
                        #     sec=now_time-prev_time
                        #     seconds=sec.total_seconds()
                        #     # if prev_status!=status or seconds > 5:
                        #     if seconds > 7:
                        #         retv, buffer1=cv2.imencode('.jpg', frame)
                        #         emp_img_string1 = buffer1.tobytes()
                        #         unknown.objects.create(status=status,image=emp_img_string1,date_time=dt_string1)
                    else:
                        if 0.977 <= confidence <=1:
                            if registration.objects.filter(id=id1).exists():
                                reg_obj = registration.objects.get(id=id1)
                                r = attendance.objects.filter(emp_id=reg_obj).order_by('-date_time').first()
                                if r==None:
                                    print('none in r none')
                                    retv, buffer1=cv2.imencode('.jpg', frame)
                                    emp_img_string1=buffer1.tobytes()
                                    attendance.objects.create(emp_id=reg_obj,status=status,image=emp_img_string1, date_time=dt_string1)
                                elif id1!='1':
                                    prev_status=r.status
                                    p_date=r.date_time
                                    prev_date=  p_date
                                    if prev_status!=status or datetime.now().astimezone().date()!=prev_date.date():
                                        retv, buffer1=cv2.imencode('.jpg', frame)
                                        emp_img_string1=buffer1.tobytes()
                                        attendance.objects.create(emp_id=reg_obj,status=status,image=emp_img_string1,date_time=dt_string1)
                                elif id1=='1':
                                    u= unknown.objects.filter().order_by('-date_time').first()
                                    if u == None:
                                        retv, buffer2=cv2.imencode('.jpg', frame)
                                        emp_img_string1 = buffer2.tobytes()
                                        unknown.objects.create(status=status,image=emp_img_string1,date_time=dt_string1)
                                    else:
                                        prev_status=u.status
                                        p_date=u.date_time
                                        prev_time=p_date
                                        now_time = datetime.now().astimezone()
                                        sec=now_time-prev_time
                                        seconds=sec.total_seconds()
                                        # if prev_status!=status or seconds > 5:
                                        if seconds > 7:
                                            retv, buffer1=cv2.imencode('.jpg', frame)
                                            emp_img_string1 = buffer1.tobytes()
                                            unknown.objects.create(status=status,image=emp_img_string1,date_time=dt_string1)
                        else:
                            pass
                            # print("You are not in")
                            # if id1=='1':
                            #     u= unknown.objects.filter().order_by('-date_time').first()
                            #     if u == None:
                            #         retv, buffer2=cv2.imencode('.jpg', frame)
                            #         emp_img_string1 = buffer2.tobytes()
                            #         unknown.objects.create(status=status,image=emp_img_string1,date_time=dt_string1)
                            #     else:
                            #         prev_status=u.status
                            #         p_date=u.date_time
                            #         prev_time=p_date
                            #         now_time=datetime_object
                            #         sec=now_time-prev_time
                            #         seconds=sec.total_seconds()
                            #         # if prev_status!=status or seconds > 5:
                            #         if seconds > 5:
                            #             retv, buffer1=cv2.imencode('.jpg', frame)
                            #             emp_img_string1 = buffer1.tobytes()
                            #             unknown.objects.create(status=status,image=emp_img_string1,date_time=dt_string1)
            
                            # else:
                            #     pass
            else:
                pass
                     
        else:
            pass

            
                                

def cam_in():   
    line_thickness = 2
    person_model = YOLO('yolov8n.pt')
    face_model = YOLO('yolov8n-face.pt')
    face_thickness =1
    queue = multiprocessing.Queue()
    recognition_process = multiprocessing.Process(target=face_recognition_process, args=(queue,))
    recognition_process.start()
    cap = cv2.VideoCapture("rtsp://admin:admin123@10.8.21.48:554/cam/realmonitor?channel=1&subtype=0")
    # cap = cv2.VideoCapture('/dev/video0')
    min_box_size_threshold = 500
    frame_count=1
    while True:
        _, imgg = cap.read()
        img=imgg[300:1500, 20:1850]
        img1 = img.copy()
        cv2.rectangle(imgg, (20, 300), (1850, 1500), (0, 255, 0), 2)  #high resolution IN
        if frame_count == 31:
            frame_count = 1                      
        if frame_count % 5 == 0:
            person_results = person_model.predict(img, verbose=False)
            for r in person_results:
                boxes = r.boxes
                for box in boxes:
                    b = box.xyxy[0]
                    c = box.cls
                    if int(c) == 0:
                        x01, y01, x02, y02 = [int(i) for i in b]
                        person_cropped_img = img[y01:y02, x01:x02]
                        box_width = x02 - x01
                        box_height = y02 - y01
                        if box_width > min_box_size_threshold or box_height > min_box_size_threshold:
                            cv2.rectangle(img, (x01, y01), (x02, y02), (0, 255, 0), line_thickness)
                          # Detect faces in the cropped person image
                            face_results = face_model.predict(img, verbose=False)
                            for r_face in face_results:
                                boxes_face = r_face.boxes
                                for box_face in boxes_face:
                                    box_cor_face = box_face.xyxy[0]
                                    c_face = box_face.cls
                                    # Check if the detected object is a face (modify class index accordingly)
                                    if int(c_face) == 0 :
                                        x1_face, y1_face, x2_face, y2_face = [int(i) for i in box_cor_face]
                                        # Adjust the coordinates based on the person bounding box
                                        cv2.rectangle(img, (x1_face, y1_face), (x2_face, y2_face), (0, 255, 0), face_thickness)
                                        dat=timezone.now()
                                        dt_string = dat.strftime("%Y-%m-%d %H:%M:%S:%f")
                                        ar=({"image":img1,"time":dt_string})
                                        
                                        queue.put(ar)
                        else:
                            pass
        frame_count += 1
        retd3, frame3 = cv2.imencode('.jpg', imgg)
        yield (b'--frame3\r\n'
                b'Content-Type: image/jpg\r\n\r\n' + frame3.tobytes() + b'\r\n')


@gzip.gzip_page
def In_cam(request):
    try:
        return StreamingHttpResponse(cam_in(), content_type="multipart/x-mixed-replace;boundary=frame")
    except Exception as e:
        print("An error occurred: ", e)
        return None








def recognition_out(queue):
    face_detector = mtcnn.MTCNN()
    path_m='facenet_keras_weights.h5'
    face_encoder= InceptionResNetV2()
    face_encoder.load_weights(path_m)
    encodings_path = 'encodings/encodings.pkl'
    encoding_dict = load_pickle(encodings_path)
    status = "OUT"
    while True:
        if not queue.empty():
            arr=queue.get()
            frame0= arr[0]
            dt_string2_out=arr[1]
            frame , data = detect(frame0,face_detector,face_encoder,encoding_dict)
            if data :
                for i in data:
                    id2 = i['id']
                    confidence = i['confidence']
                    if id2 =='1'and confidence =='unknown':
                        u= unknown.objects.filter().order_by('-date_time').first()
                        if u == None:
                            retv, buffer2=cv2.imencode('.jpg', frame)
                            emp_img_string1 = buffer2.tobytes()
                            unknown.objects.create(status=status,image=emp_img_string1,date_time=dt_string2_out)
                        else:
                            # prev_status=u.status
                            p_date_out=u.date_time
                            print(p_date_out,">>>>>>>>!!!!!!!!!33333333333333333!!!!!!!!!>>>>>>>>>>>>>>>")
                            prev_time_out=p_date_out
                            now_time_out = datetime.now().astimezone()
                            sec=now_time_out-prev_time_out
                            seconds_out=sec.total_seconds()
                            # if prev_status!=status or seconds > 5:
                            if seconds_out > 7:
                                retv, buffer1=cv2.imencode('.jpg', frame)
                                emp_img_string1 = buffer1.tobytes()
                                unknown.objects.create(status=status,image=emp_img_string1,date_time=dt_string2_out)
                    else:
                        if 0.977 <= confidence <=1:
                            reg_obj_out = registration.objects.get(id=id2)
                            r_out = attendance.objects.filter(emp_id=reg_obj_out).order_by('-date_time').first()
                            if (id2!='1' and r_out!=None):
                                prev_status_out=r_out.status
                                prev_date_out=r_out.date_time.date()
                                current_date_out= timezone.now().date()
                                if prev_status_out=='IN' and prev_date_out == current_date_out:
                                    retv_out, buffer2_out=cv2.imencode('.jpg', frame)
                                    emp_img_string2_out=buffer2_out.tobytes()
                                    attendance.objects.create(emp_id=reg_obj_out,status=status,image=emp_img_string2_out,date_time=dt_string2_out)
                                    
                                    
                            elif id2=='1':
                                u_out= unknown.objects.filter().order_by('-date_time').first()
                                if u_out == None:
                                    retv_out, imag_out=cv2.imencode('.jpg', frame)
                                    emp_img_string2_out = imag_out.tobytes()
                                    unknown.objects.create(status=status,image=emp_img_string2_out,date_time=dt_string2_out)
                                else:
                                    # prev_status_out=u_out.status
                                    p_date_out=u_out.date_time
                                    print(p_date_out,">>>>>>>>!!!!!!!!44444444444444!!!!!!!!!!>>>>>>>>>>>>>>>")
                                    prev_time_out=p_date_out
                                    now_time_out = datetime.now().astimezone()
                                    sec_out=now_time_out-prev_time_out
                                    seconds_out=sec_out.total_seconds()
                                    # print(seconds_out,"???????????????")
                                    
                                    # if prev_status_out!=status or seconds_out > 5:
                                    if seconds_out > 7:
                                        retv_out, imag3_out=cv2.imencode('.jpg', frame)
                                        emp_img_string2_out = imag3_out.tobytes()
                                        unknown.objects.create(status=status,image=emp_img_string2_out,date_time=dt_string2_out)
                        else:
                            pass
                            # if id2=='1':
                            #     u_out= unknown.objects.filter().order_by('-date_time').first()
                            #     if u_out == None:
                            #         retv_out, buffer2_out=cv2.imencode('.jpg', frame)
                            #         emp_img_string1_out = buffer2_out.tobytes()
                            #         unknown.objects.create(status=status,image=emp_img_string1_out,date_time=dt_string2_out)
                            #     else:
                            #         prev_status_out=u_out.status
                            #         p_date_out=u_out.date_time
                            #         prev_time_out=p_date_out
                            #         now_time_out=datetime_object
                            #         sec_out=now_time_out-prev_time_out
                            #         seconds_out=sec_out.total_seconds()
                                    
                            #         # if prev_status_out!=status or seconds_out > 5:
                            #         if seconds_out > 5:
                            #             retv_out, buffer1_out=cv2.imencode('.jpg', frame)
                            #             emp_img_string1_out = buffer1_out.tobytes()
                            #             unknown.objects.create(status=status,image=emp_img_string1_out,date_time=dt_string2_out)
                            # else:
                            #     pass
            else:
                pass
        else:
            pass

def cam_out():
    line_thickness = 2
    person_model = YOLO('yolov8n.pt')
    face_model = YOLO('yolov8n-face.pt')
    face_thickness =1
    queue = multiprocessing.Queue() 
    recog_out = multiprocessing.Process(target=recognition_out, args=(queue,))
    recog_out.start()
    cap = cv2.VideoCapture("rtsp://admin:admin123@10.8.21.47:554/cam/realmonitor?channel=1&subtype=0")
    # cap = cv2.VideoCapture('/dev/video0')
    min_box_size_threshold = 500
    frame_count=1
    while True:
        _, imgg = cap.read()
        img=imgg[800:1500, 10:2300]
        img1 = img.copy()
        cv2.rectangle(imgg, (10, 800), (2300, 1500), (0, 255, 0), 2)  #high resolution OUT
        
        if frame_count == 31:
            frame_count = 1                      
        if frame_count % 5 == 0:
            person_results = person_model.predict(img ,verbose=False)
            for r in person_results:
                boxes = r.boxes
                for box in boxes:
                    b = box.xyxy[0]
                    c = box.cls
                    if int(c) == 0:
                        x01, y01, x02, y02 = [int(i) for i in b]
                        person_cropped_img = img[y01:y02, x01:x02]
                        box_width = x02 - x01
                        box_height = y02 - y01
                        if box_width > min_box_size_threshold or box_height > min_box_size_threshold:
                            print("Person detected.")
                            cv2.rectangle(img, (x01, y01), (x02, y02), (0, 255, 0), line_thickness)
                        
                          # Detect faces in the cropped person image
                            face_results = face_model.predict(img, verbose=False)
                            for r_face in face_results:
                                boxes_face = r_face.boxes
                                for box_face in boxes_face:
                                    box_cor_face = box_face.xyxy[0]
                                    c_face = box_face.cls
                                    # Check if the detected object is a face (modify class index accordingly)
                                    if int(c_face) == 0 :
                                        print("Person face detected")
                                        x1_face, y1_face, x2_face, y2_face = [int(i) for i in box_cor_face]
                                        # Adjust the coordinates based on the person bounding box
                                        cv2.rectangle(img, (x1_face, y1_face), (x2_face, y2_face), (0, 255, 0), face_thickness)
                                        dat=timezone.now()
                                        dt_string = dat.strftime("%Y-%m-%d %H:%M:%S:%f")
                                        ar_out=(img1,dt_string)
                                        queue.put(ar_out)
                        else:
                            pass
        frame_count += 1
        retd3, frame3 = cv2.imencode('.jpg', imgg)
        yield (b'--frame3\r\n'
                b'Content-Type: image/jpg\r\n\r\n' + frame3.tobytes() + b'\r\n')


@gzip.gzip_page
def Out_cam(request):
    try:
        return StreamingHttpResponse(cam_out(), content_type="multipart/x-mixed-replace;boundary=frame")
    except Exception as e:
        print("An error occurred: ", e)
        return None















# def cam_out():
#     face_detector = cv2.FaceDetectorYN.create("yunet_22mar.onnx", "", (160, 160))
#     line_thickness = 1
#     edge_thickness=1
#     encodings_path = 'encodings/encodings.pkl'
#     encoding_dict = load_pickle(encodings_path)
#     recognition_t = 0.3
#     l2_normalizer = Normalizer('l2')
#     required_shape = (160, 160)

#     def recognition_out(queue_out):
#         face_encoder_out = InceptionResNetV2()
#         face_encoder_out.load_weights("facenet_keras_weights.h5")

#         status_out = "OUT"
#         dat_out = timezone.now()
#         dt_string2_out = dat_out.strftime("%Y-%m-%d %H:%M:%S:%f")

#         while True:
#             if not queue_out.empty():
#                 arr_out=queue_out.get()
#                 # print(arr[1])
#                 face_img_out = arr_out[0]
#                 face_normalized_out = normalize(face_img_out)
#                 face_resized_out = cv2.resize(face_normalized_out, required_shape)
#                 face_d_out = np.expand_dims(face_resized_out, axis=0)
#                 encode_out = face_encoder_out.predict(face_d_out, verbose=False)
#                 encode_out = np.sum(encode_out, axis=0)
#                 encode_out = np.expand_dims(encode_out, axis=0)
#                 encode_out = l2_normalizer.transform(encode_out.reshape(1, -1))[0]
#                 min_distance_out = float('inf')
#                 id2 = '1'

#                 for db_name_out, db_encode_out in encoding_dict.items():
#                     dist_out = cosine(db_encode_out, encode_out)
#                     if dist_out < recognition_t and dist_out < min_distance_out:
#                         id2 = db_name_out
#                         min_distance_out = dist_out

#                 if 0.950 <= arr_out[1] <= 1:
#                     # if registration.objects.filter(id=id2).exists():
#                     reg_obj_out = registration.objects.get(id=id2)
#                     r_out = attendance.objects.filter(emp_id=reg_obj_out).order_by('-date_time').first()
#                     if (id2!='1' and r_out!=None):
#                         prev_status_out=r_out.status
#                         prev_date_out=r_out.date_time.date()
#                         current_date_out= timezone.now().date()
#                         if prev_status_out=='IN' and prev_date_out == current_date_out:
#                             retv_out, buffer2_out=cv2.imencode('.jpg', arr_out[2])
#                             emp_img_string2_out=buffer2_out.tobytes()
#                             attendance.objects.create(emp_id=reg_obj_out,status=status_out,image=emp_img_string2_out,date_time=dt_string2_out)
                
#                     # elif (id2=='1' and r_out==None):
#                     #     retv_out, imag1_out=cv2.imencode('.jpg', arr_out[2])
#                     #     emp_img_string2_out = imag1_out.tobytes()
#                     #     unknown.objects.create(status=status_out,image=emp_img_string2_out,date_time=dt_string2_out)
                            
#                     elif id2=='1':
#                         u_out= unknown.objects.filter().order_by('-date_time').first()
#                         if u_out == None:
#                             retv_out, imag_out=cv2.imencode('.jpg', arr_out[2])
#                             emp_img_string2_out = imag_out.tobytes()
#                             unknown.objects.create(status=status_out,image=emp_img_string2_out,date_time=dt_string2_out)
#                         else:
#                             prev_status_out=u_out.status
#                             p_date_out=u_out.date_time
#                             prev_time_out=p_date_out
#                             now_time_out=datetime.now().astimezone()
#                             sec_out=now_time_out-prev_time_out
#                             seconds_out=sec_out.total_seconds()
#                             # if prev_status_out!=status_out or seconds_out > 5:
#                             if prev_status_out!=status_out or seconds_out > 20:
#                                 retv_out, imag3_out=cv2.imencode('.jpg', arr_out[2])
#                                 emp_img_string2_out = imag3_out.tobytes()
#                                 unknown.objects.create(status=status_out,image=emp_img_string2_out,date_time=dt_string2_out)
#                 else:
#                     if id2=='1':
#                         u_out= unknown.objects.filter().order_by('-date_time').first()
#                         if u_out == None:
#                             retv_out, buffer2_out=cv2.imencode('.jpg', arr_out[2])
#                             emp_img_string1_out = buffer2_out.tobytes()
#                             unknown.objects.create(status=status_out,image=emp_img_string1_out,date_time=dt_string2_out)
#                         else:
#                             prev_status_out=u_out.status
#                             p_date_out=u_out.date_time
#                             prev_time_out=p_date_out
#                             now_time_out=datetime.now().astimezone()
#                             sec_out=now_time_out-prev_time_out
#                             seconds_out=sec_out.total_seconds()
#                             # if prev_status_out!=status_out or seconds_out > 5:
#                             if prev_status_out!=status_out or seconds_out > 20:
#                                 retv_out, buffer1_out=cv2.imencode('.jpg', arr_out[2])
#                                 emp_img_string1_out = buffer1_out.tobytes()
#                                 unknown.objects.create(status=status_out,image=emp_img_string1_out,date_time=dt_string2_out)
#                     # else:
#                     #     pass

#     queue_out = multiprocessing.Queue() 
#     recog_out = multiprocessing.Process(target=recognition_out, args=(queue_out,))
#     recog_out.start()
    
#     # cap_out = cv2.VideoCapture(0)
#     # cap = cv2.VideoCapture('/dev/video0')
#     cap_out = cv2.VideoCapture("rtsp://admin:admin123@10.8.21.47:554/cam/realmonitor?channel=1&subtype=0")
    

#     while cap_out.isOpened():
#         ret_out, fram_out = cap_out.read()
#         if not ret_out:
#             print("Camera not opened")
#             break

#         frame_out=fram_out[450:1050, 10:1675]
#         cv2.rectangle(fram_out, (10, 450), (1675, 1050), (0, 255, 0), 2)

#         img_RGB_out = cv2.cvtColor(frame_out, cv2.COLOR_BGR2RGB)
#         height_out, width_out, _ = img_RGB_out.shape
#         face_detector.setInputSize((width_out, height_out))
#         _, faces_out = face_detector.detect(img_RGB_out)
#         if faces_out is not None:
#             for face_out in faces_out:
#                 face_confidence_out = float(face_out[-1])
#                 confidence_out = decimal.Decimal(face_confidence_out).quantize(decimal.Decimal('0.0001'), rounding=decimal.ROUND_DOWN)
#                 x1_out, y1_out, w_out, h_out = list(map(int, face_out[:4]))
#                 x1_out, y1_out = abs(x1_out), abs(y1_out)
#                 x2_out, y2_out = x1_out + w_out, y1_out + h_out
#                 face_img_out = img_RGB_out[y1_out:y2_out, x1_out:x2_out]
#                 ar_out=(face_img_out, confidence_out, frame_out)
#                 queue_out.put(ar_out)

#                 cv2.rectangle(frame_out, (x1_out, y1_out), (x2_out, y2_out), (0, 255, 0), line_thickness)
#                 cv2.putText(frame_out, f"{w_out}, {h_out}" , (x1_out, y1_out - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
#                 cv2.line(frame_out, (x1_out, y1_out), (x1_out + int(w_out/4), y1_out), (0, 255, 255), edge_thickness)
#                 cv2.line(frame_out, (x1_out, y1_out), (x1_out, y1_out + int(h_out/4)), (0, 255, 0), edge_thickness)
#                 cv2.line(frame_out, (x1_out + int(3*w_out/4), y1_out), (x2_out, y1_out), (0, 255, 0), edge_thickness)
#                 cv2.line(frame_out, (x2_out, y1_out + int(h_out/4)), (x2_out, y1_out), (0, 255, 255), edge_thickness)
#                 cv2.line(frame_out, (x1_out, y1_out + int(3*h_out/4)), (x1_out, y2_out), (0, 255, 255), edge_thickness)
#                 cv2.line(frame_out, (x1_out + int(w_out/4), y2_out), (x1_out, y2_out), (0, 255, 0), edge_thickness)
#                 cv2.line(frame_out, (x1_out + int(3*w_out/4), y2_out), (x2_out, y2_out), (0, 255, 255), edge_thickness)
#                 cv2.line(frame_out, (x2_out, y2_out - int(h_out/4)), (x2_out, y2_out), (0, 255, 0), edge_thickness)


#         retd_out3, frame3_out = cv2.imencode('.jpg', fram_out)
#         yield (b'--frame3\r\n'
#                 b'Content-Type: image/jpg\r\n\r\n' + frame3_out.tobytes() + b'\r\n')

#     recog_out.join()
#     cap_out.release()


# @gzip.gzip_page
# def Out_cam(request):
#     try:
#         return StreamingHttpResponse(cam_out(), content_type="multipart/x-mixed-replace;boundary=frame")
#     except Exception as e:
#         print("An error occurred: ", e)
#         return None


def tot_time(in_times, out_times):
    sum=0
    for i in range(len(out_times)):
        out_dt=out_times[i]
        in_dt=in_times[i]
        tot=out_dt-in_dt
        t=tot.total_seconds()
        sum+=t
        tm=sum/3600
        rtm=(tm, 2)
        return rtm


def report(request):
    if request.method == 'POST':
        try:
            emp_id = request.POST.get('emp_id')
            department = request.POST.get('department')
            name = request.POST.get('name')
            search_params = {}
            if emp_id:
                search_params['id'] = emp_id
            if department:
                search_params['department'] = department
            if name:
                search_params['name'] = name
            results = registration.objects.filter(**search_params)
            data = json.dumps(list(results.values()), default=str)
            return JsonResponse({'results': data}, safe=False)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)})
 
    if request.method == 'GET':
        a = datetime.now().date()
        today = a
        ignored_id = 1
        registrations = registration.objects.filter(attendance__date_time__startswith=today).exclude(id=ignored_id)
 
        # Annotate the queryset
        registrations = registrations.annotate(
            first_in=Coalesce(Min('attendance__date_time', filter=Q(attendance__status='IN')), Value(None)),
            last_out=Coalesce(Max('attendance__date_time', filter=Q(attendance__status='OUT')), Value(None)),
            in_count=Count('attendance', filter=Q(attendance__status='IN')),
            out_count=Count('attendance', filter=Q(attendance__status='OUT')),
        ).values('id', 'name', 'department', 'first_in', 'last_out', 'in_count', 'out_count')
 
        # Convert UTC to IST for first_in and last_out
# Convert UTC to IST for first_in and last_out in 12-hour format
# Convert UTC to IST for first_in and last_out in 12-hour format
        ist = pytz.timezone('Asia/Kolkata')  # Change 'Asia/Kolkata' to the desired timezone
        for index, reg in enumerate(registrations):
            if reg['first_in']:
                registrations[index]['first_in'] = reg['first_in'].replace(tzinfo=pytz.utc).astimezone(ist).strftime('%Y-%m-%d %I:%M:%S %p')
            if reg['last_out']:
                registrations[index]['last_out'] = reg['last_out'].replace(tzinfo=pytz.utc).astimezone(ist).strftime('%Y-%m-%d %I:%M:%S %p')
        paginator = Paginator(registrations, 20)
        page_num = request.GET.get('page')
 
        try:
            paginated_data = paginator.get_page(page_num)
        except EmptyPage:
            paginated_data = paginator.get_page(1)
 
        context = {'data': paginated_data}
        return render(request, 'home/reporting.html', context)


def User_report(request, id):
    if request.method == "POST":
        current_date = request.POST.get('date')
        uid = int(id)
        rdata = registration.objects.get(id=uid)
        user_attendance = attendance.objects.filter(emp_id=uid, date_time__contains=current_date)
        in_count = user_attendance.filter(status='IN').count()
        out_count = user_attendance.filter(status='OUT').count()
        in_times = user_attendance.filter(status='IN').values_list('date_time', flat=True)
        out_times = user_attendance.filter(status='OUT').values_list('date_time', flat=True)
        total_time_seconds = 0
        for i in range(len(out_times)):
            out_dt = out_times[i]
            out_date_time=out_dt
            in_dt = in_times[i]
            in_date_time=in_dt
            tot = out_date_time - in_date_time
            total_time_seconds += tot.total_seconds()
        total_time_hours = round(total_time_seconds / 3600, 2)
        image_data = rdata.image
        context = {'imgdata': base64.b64encode(image_data).decode('utf-8')}
        return render(request, 'home/user_details.html', {
            'rdata': rdata,
            'Cin': in_count,
            'Cout': out_count,
            'out_times': out_times,
            'in_times': in_times, 
            'total_time': total_time_hours,
            'context': context
        })
    try:
        uid = int(id)
        rdata = registration.objects.get(id=uid)
        current_date = datetime.now().strftime('%Y-%m-%d')
        user_attendance = attendance.objects.filter(emp_id=uid, date_time__contains=current_date)
        in_count = user_attendance.filter(status='IN').count()
        out_count = user_attendance.filter(status='OUT').count()
        in_times = user_attendance.filter(status='IN').values_list('date_time', flat=True)
        out_times = user_attendance.filter(status='OUT').values_list('date_time', flat=True)
        indian_tz = pytz.timezone('Asia/Kolkata')
        indian_in_times = []
        indian_out_times = []
        for in_time in in_times:
            utc_time = in_time + timedelta(hours=5, minutes=30) 
            indian_time = utc_time.astimezone(indian_tz)
            indian_in_times.append(indian_time)
        for out_time in out_times:
            utc_time = out_time + timedelta(hours=5, minutes=30) 
            indian_time = utc_time.astimezone(indian_tz)
            indian_out_times.append(indian_time)
        total_time_seconds = 0
        for i in range(len(indian_out_times)):
            out_dt = indian_out_times[i]
            in_dt = indian_in_times[i]
            tot = out_dt - in_dt
            total_time_seconds += tot.total_seconds()
        total_time_hours = round(total_time_seconds / 3600, 2)
        image_data = rdata.image
        context = {'imgdata': base64.b64encode(image_data).decode('utf-8')}
        return render(request, 'home/user_details.html', {
            'rdata': rdata,
            'Cin': in_count,
            'Cout': out_count,
            'out_times': indian_out_times,
            'in_times': indian_in_times,
            'total_time': total_time_hours,
            'context': context
        })
    except registration.DoesNotExist:
        return HttpResponseNotFound('User not found')
    except Exception as e:
        uid = int(id)
        rdata = registration.objects.get(id=uid)
        today = date.today()
        user_attendance = attendance.objects.filter(emp_id=uid, date_time__date=today)
        in_count = user_attendance.filter(status='IN').count()
        out_count = 0
        in_times = user_attendance.filter(status='IN').values_list('date_time', flat=True)
        out_times = []
        total_time_hours = "--"
        sr="--"
        image_data = rdata.image
        context = {'imgdata': base64.b64encode(image_data).decode('utf-8')}
        return render(request, 'home/user_details.html', {
            'rdata': rdata,
            'Cin': in_count,
            'Cout': out_count,
            'in_times':in_times,
            'out_times':out_times,
            'total_time': sr,
            'context': context
        })


def calender(request):
    if request.method=="POST":
        id = request.POST.get("id")
        date = request.POST.get("date")
        result = get_monthly_attendance(id)
    return render(request,"home/calender.html")


def get_monthly_attendance(employee_id):
    now = datetime.now()
    year = now.year
    month = now.month

    result = attendance.objects \
        .annotate(month=TruncMonth('date_time')) \
        .filter(emp_id_id=employee_id, month__year=year, month__month=month) \
        .values('month') \
        .annotate(total_attendance=Count('status')) \
        .values('month', 'total_attendance')

    return result


def attendance_report(request):
    current_date = datetime.now().date()
    try:
        start_date = attendance.objects.earliest('date_time__date').date_time.date()
    except ObjectDoesNotExist:
        start_date = current_date 
    attendance_status_list = []
    while start_date <= current_date:
        next_date = start_date + timedelta(days=1)

        attendance_list = registration.objects.annotate(
            attendance_count=Count(
                'attendance',
                filter=models.Q(
                    attendance__date_time__date=start_date,
                    attendance__status='IN'
                )
            )
        ).exclude(id=1).values('id', 'name', 'department', 'attendance_count')
        total_users = registration.objects.exclude(id=1).aggregate(count=Count('id'))['count']

        present_count = 0
        absent_count = 0

        for att in attendance_list:
            attendance_count = att['attendance_count']
            if attendance_count > 0:
                attendance_status = 'Present'
                present_count += 1
            else:
                attendance_status = 'Absent'
                absent_count += 1

        attendance_status_list.append({
            'title': f"{present_count} Present",
            'start': start_date.strftime('%Y-%m-%d'),
            'end': next_date.strftime('%Y-%m-%d'),
            "backgroundColor": "green",
        })
        attendance_status_list.append({
            'title': f"{absent_count} Absent",
            'start': start_date.strftime('%Y-%m-%d'),
            'end': next_date.strftime('%Y-%m-%d'),
            "backgroundColor": "red",
        })
        attendance_status_list.append({
            'title': f"{total_users} total",
            'start': start_date.strftime('%Y-%m-%d'),
            'end': next_date.strftime('%Y-%m-%d'),
            "backgroundColor": "blue",
        })

        start_date = next_date

    context = {
        "events": attendance_status_list,
    }
    return render(request, 'home/attendance_report.html', context)


@csrf_exempt
def get_attendance_events(request):
    attendance_events = attendance.objects.all()
    data = []
    for event in attendance_events:
        data.append({
            'title': event.emp_id.name,
            'start': event.date_time.date().isoformat(),
            'end': event.date_time.date().isoformat(),
            'status': event.status
        })
    return JsonResponse(data, safe=False)


def fetch_employees(request):
    department = request.GET.get('department')
    if department:
        employees = registration.objects.filter(department=department).values('id', 'name')
        return JsonResponse(list(employees), safe=False)
    return JsonResponse({'error': 'Invalid department'}, status=400)


def attendance_view(request):
    list_data = []
    if request.method == 'GET':
        employee_id = request.GET.get('employeeId')
        attendance_data = []
        attendance_data, attendance_list = get_attendance_data(employee_id)
        for entry in attendance_data:
            date = entry['date']
            attendance_count = entry['attendance_count']
        for i in attendance_list:
            s_date = i["date"]
            c_date = datetime.strptime(s_date, "%Y-%m-%d").date()
            next_date = c_date + timedelta(days=1)   
            str_c_date = c_date.strftime("%Y-%m-%d")
            str_next_date = next_date.strftime("%Y-%m-%d")
            if i["status"] == "Absent":
                data = {
                    "title": i["status"],
                    "start": str_c_date,
                    "end": str_next_date,
                    "backgroundColor": "red"
                }
                list_data.append(data)
            else:
                data = {
                    "title": i["status"],
                    "start": str_c_date,
                    "end": str_next_date,
                    "backgroundColor": "green",
                }
                list_data.append(data)
        del list_data[-1]
        return JsonResponse(list_data, safe=False)


def get_attendance_data(employee_id):
    start_date = attendance.objects.earliest('date_time__date').date_time.date()
    current_date = timezone.now().date()
    attendance_data = registration.objects.filter(
        id=employee_id,
        attendance__date_time__range=(start_date, current_date)).annotate(
        attendance_count=Count('attendance'),
        date=models.functions.TruncDate('attendance__date_time')).values('id', 'name', 'department', 'attendance_count', 'date')
    attendance_status_list = []
    date_range = range((current_date - start_date).days + 1)
    for i in date_range:
        date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        attendance_count = 0
        for entry in attendance_data:
            if entry['date'].strftime('%Y-%m-%d') == date:
                attendance_count = entry['attendance_count']
                break

        attendance_status = 'Present' if attendance_count > 0 else 'Absent'
        attendance_status_list.append({
            'date': date,
            'status': attendance_status
        })

    return attendance_data, attendance_status_list


def unknown_view(request):
    u = unknown.objects.all().order_by('-date_time')

    context = {'data': []}

    if request.method == 'POST':
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        today = date.today()
        year = today.year
        month = today.month
        day = today.day
        start_date_week = today - timedelta(days=today.weekday())
        end_date_week = start_date_week + timedelta(days=6)
        start_date_month = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date_month = date(year, month, last_day)
        start_date_6_months = today - timedelta(days=180)

        if start_date and end_date:
            u = unknown.objects.filter(date_time__date__range=[start_date, end_date])
        elif day:
            u = unknown.objects.filter(created_at__year=year, created_at__month=month, created_at__day=day)
        elif start_date_week and end_date_week:
            u = unknown.objects.filter(date_time__date__range=(start_date_week, end_date_week))
        elif start_date_month and end_date_month:
            u = unknown.objects.filter(date_time__date__range=(start_date_month, end_date_month))
        elif start_date_6_months and today:
            u = unknown.objects.filter(date_time__date__range=(start_date_6_months, today))
        else:
            u = unknown.objects.none()

    # Convert UTC to IST
    ist = pytz.timezone('Asia/Kolkata')
    for item in u:
        item.date_time = item.date_time.replace(tzinfo=pytz.utc).astimezone(ist).strftime('%Y-%m-%d %I:%M:%S %p')


    # Pagination
    paginator = Paginator(u, 50)
    page_num = request.GET.get('page')

    try:
        paginated_data = paginator.get_page(page_num)
    except EmptyPage:
        paginated_data = paginator.get_page(1)

    for item in paginated_data:
        image_data = item.image
        image_data_base64 = base64.b64encode(image_data).decode('utf-8')
        context['data'].append({'item': item, 'image_data_base64': image_data_base64})

    context['paginated_data'] = paginated_data
    return render(request, "home/unknown_attendance.html", context)


def delete_selected_unknowns(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('ids[]')
 
        # Delete selected items from unknown model
        unknown_objects = unknown.objects.filter(id__in=selected_ids)
        unknown_objects.delete()
 
        # Delete corresponding items from rejected_unknown model
        for obj in unknown_objects:
            rejected_instance = rejected_unknown.objects.create(
                status=obj.status,
                date_time=obj.date_time,
                image=obj.image
            )
            rejected_instance.save()
 
        return JsonResponse({'message': 'Items deleted successfully.'})
 
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def check_employee_presence(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        data = json.loads(body)
        employee_ids = data.get('employeeIds', [])
        employee_data = []
        start_date = attendance.objects.earliest('date_time__date').date_time.date()
        current_date = timezone.now().date()

        while start_date <= current_date:
            next_date = start_date + timedelta(days=1)
            present_count = 0
            absent_count = 0
            total = 0

            for employee_id in employee_ids:
                employee_attendance = attendance.objects.filter(emp_id=employee_id, date_time__date=start_date)
                count_present = employee_attendance.filter(status='IN').count()

                if count_present > 0:
                    present_count += 1
                    total += 1
                else:
                    absent_count += 1
                    total += 1

            employee_data.append({
                'title': f"{present_count} Present",
                'start': start_date.strftime('%Y-%m-%d'),
                'end': next_date.strftime('%Y-%m-%d'),
                'backgroundColor': 'green'
            })
            employee_data.append({
                'title': f"{absent_count} Absent",
                'start': start_date.strftime('%Y-%m-%d'),
                'end': next_date.strftime('%Y-%m-%d'),
                'backgroundColor': 'red'
            })
            employee_data.append({
                'title': f"{total} Total",
                'start': start_date.strftime('%Y-%m-%d'),
                'end': next_date.strftime('%Y-%m-%d'),
                'backgroundColor': 'blue'
            })

            start_date = next_date

        return JsonResponse(employee_data, safe=False)


@csrf_exempt
def calender_event_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            event_data = data.get('eventData')
            startdate_str = event_data['start']
            start_date = datetime.strptime(startdate_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            start_date = start_date.replace(tzinfo=pytz.utc)  # Set input time to UTC
            start_date_ist = start_date.astimezone(pytz.timezone('Asia/Kolkata'))  # Convert to IST
            title = event_data['title']
            send_department = data.get('department')
            source = data.get('source')
            employee_data = []

            if event_data and not send_department and not source and "Present" in title:
                employee_ids = list(attendance.objects.filter(status='IN', date_time__date=start_date_ist.date()).values_list('emp_id', flat=True).distinct())
                employee_data = []

                for emp_id1 in employee_ids:
                    employee = registration.objects.get(id=emp_id1)

                    first_in_attendance = attendance.objects.filter(emp_id=employee, status='IN', date_time__date=start_date_ist.date())
                    if first_in_attendance.exists():
                        first_in_time = first_in_attendance.earliest('date_time').date_time.astimezone(pytz.timezone('Asia/Kolkata')).time()
                        first_in_time = first_in_time.strftime('%I:%M:%S %p')
                    else:
                        first_in_time = "--"

                    last_out_attendance = attendance.objects.filter(emp_id=employee, status='OUT', date_time__date=start_date_ist.date())
                    if last_out_attendance.exists():
                        last_out_time = last_out_attendance.latest('date_time').date_time.astimezone(pytz.timezone('Asia/Kolkata')).time()
                        last_out_time = last_out_time.strftime('%I:%M:%S %p')
                    else:
                        last_out_time = "--"

                    employee_data.append({
                        'id': employee.id,
                        'name': employee.name,
                        'date': start_date_ist.strftime('%Y-%m-%d'),
                        'first_in_time': first_in_time,
                        'last_out_time': last_out_time,
                        'status': 'Present'
                    })

                # Sort the employee_data list by 'first_in_time'
                employee_data = sorted(employee_data, key=lambda x: x['first_in_time'], reverse=True)

                if not employee_data:
                    print("No attendance records found for the specified conditions.")

            elif event_data and not send_department and not source and "Absent" in title:
                employees = registration.objects.all().exclude(id=1)
                for employee in employees:
                    attendance_records = attendance.objects.filter(emp_id=employee, date_time__date=start_date_ist.date())
                    if not attendance_records.exists():
                        employee_data.append({
                            'id': employee.id,
                            'name': employee.name,
                            'date': start_date_ist.strftime('%Y-%m-%d'),
                            'first_in_time': '--',
                            'last_out_time': '--',
                            'status': 'Absent'
                        })

            elif event_data and not send_department and not source and "total" in title:
                print("Entering Total section")
                employees = registration.objects.all().exclude(id=1)
                
                # List to store employee data
                employee_data = []

                for employee in employees:
                    print(f"Processing employee: {employee.name}")
                    attendance_records = attendance.objects.filter(emp_id=employee, date_time__date=start_date_ist.date())

                    if attendance_records.exists():
                        first_in_time = attendance_records.filter(status='IN').earliest('date_time').date_time.astimezone(pytz.timezone('Asia/Kolkata')).strftime('%I:%M:%S %p')
                        
                        last_out_records = attendance_records.filter(status='OUT')
                        if last_out_records.exists():
                            last_out_time = last_out_records.latest('date_time').date_time.astimezone(pytz.timezone('Asia/Kolkata')).strftime('%I:%M:%S %p')
                        else:
                            last_out_time = "--"

                        status = 'Present'
                    else:
                        first_in_time = "--"
                        last_out_time = "--"
                        status = 'Absent'

                    employee_data.append({
                        'id': employee.id,
                        'name': employee.name,
                        'date': start_date_ist.strftime('%Y-%m-%d'),
                        'first_in_time': first_in_time,
                        'last_out_time': last_out_time,
                        'status': status
                    })

                # Sort employee_data based on 'status' key
                employee_data = sorted(employee_data, key=lambda x: (x['status'], x['first_in_time'] if x['status'] == 'Present' else ''), reverse=True)

                # Print the sorted employee data
                for employee_info in employee_data:
                    print(f"ID: {employee_info['id']}, Name: {employee_info['name']}, Status: {employee_info['status']}, First In Time: {employee_info['first_in_time']}, Last Out Time: {employee_info['last_out_time']}")
            elif event_data and send_department and not source and "Present" in title:
                department_name = send_department  
                employees = registration.objects.filter(department=department_name).exclude(id=1)
                employee_data = []
                for employee in employees:
                    attendance_records = attendance.objects.filter(emp_id=employee, date_time__date=exect_date, status='IN')
                    if attendance_records.exists():
                        first_in_time = attendance_records.earliest('date_time').date_time
                        last_out_attendance = attendance.objects.filter(emp_id=employee, status='OUT', date_time__date=exect_date)
                        if last_out_attendance.exists():
                            last_out_time = last_out_attendance.latest('date_time').date_time
                        else:
                            last_out_time = "--"
                        employee_data.append({
                            'id': employee.id,
                            'name': employee.name,
                            'department': employee.department,
                            "date": exect_date,
                            'first_in_time': first_in_time,
                            'last_out_time': last_out_time,
                            'status': 'Present'
                        })
            elif event_data and send_department and not source and "Absent" in title:
                department_name = send_department 
                employees = registration.objects.filter(department=department_name).exclude(id=1)
                employee_data = []
                for employee in employees:
                    attendance_records = attendance.objects.filter(emp_id=employee, date_time__date=exect_date)
                    if not attendance_records.exists():
                        employee_data.append({
                            'id': employee.id,
                            'name': employee.name,
                            'department': employee.department,
                            "date": exect_date,
                            'first_in_time': '--',
                            'last_out_time': '--',
                            'status': 'Absent'
                        })
            elif event_data and send_department and not source and "Total" in title:
                department_name = send_department  
                employees = registration.objects.filter(department=department_name).exclude(id=1)
                for employee in employees:
                    attendance_records = attendance.objects.filter(emp_id=employee, date_time__date=exect_date)
                    if attendance_records.exists():
                        first_in_attendance = attendance.objects.filter(emp_id=employee, status='IN', date_time__date = exect_date)
                        if first_in_attendance.exists():
                            first_in_time = first_in_attendance.earliest('date_time').date_time
                        else:
                            first_in_time = "--"
                        last_out_attendance = attendance.objects.filter(emp_id=employee, status='OUT', date_time__date = exect_date)
                        if last_out_attendance.exists():
                            last_out_time = last_out_attendance.latest('date_time').date_time
                        else:
                            last_out_time = "--"
                        employee_data.append({
                            'id': employee.id,
                            'name': employee.name,
                            'department': employee.department,
                            "date": exect_date,
                            'first_in_time': first_in_time,
                            'last_out_time': last_out_time,
                            'status': 'Present'
                        })
                    else:
                        employee_data.append({
                            'id': employee.id,
                            'name': employee.name,
                            'department': employee.department,
                            "date": exect_date,
                            'first_in_time': '--',
                            'last_out_time': '--',
                            'status': 'Absent',
                        })
            elif event_data and send_department and source and "Present" in title:
                department_name = send_department  
                employee_id = source  
                employee = registration.objects.get(department=department_name, id=employee_id)
                attendance_records = attendance.objects.filter(emp_id=employee, date_time__date=exect_date, status='IN')
                if attendance_records.exists():
                    first_in_time = attendance_records.earliest('date_time').date_time
                    last_out_attendance = attendance.objects.filter(emp_id=employee, status='OUT', date_time__date=exect_date)
                    if last_out_attendance.exists():
                        last_out_time = last_out_attendance.latest('date_time').date_time
                    else:
                        last_out_time = "--"
                    employee_data.append({
                        'id': employee.id,
                        'name': employee.name,
                        'department': employee.department,
                        "date": exect_date,
                        'first_in_time': first_in_time,
                        'last_out_time': last_out_time,
                        'status': 'Present'
                    })
                    
                else:
                    employee_data.append({
                        'id': employee.id,
                        'name': employee.name,
                        'department': employee.department,
                        "date": exect_date,
                        'first_in_time': '--',
                        'last_out_time': '--',
                        'status': 'Absent'
                    })
            elif event_data and send_department and source and "Absent" in title:
                department_name = send_department  
                employee_id = source
                employee = registration.objects.get(department=department_name, id=employee_id)
                attendance_records = attendance.objects.filter(emp_id=employee, date_time__date=exect_date)
                if not attendance_records.exists():
                    employee_data.append({
                        'id': employee.id,
                        'name': employee.name,
                        'department': employee.department,
                        "date": exect_date,
                        'first_in_time': '--',
                        'last_out_time': '--',
                        'status': 'Absent'
                    })
            return JsonResponse({'data': employee_data})
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            print(str(e))  
            return JsonResponse({'message': 'An error occurred while processing the data.'}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method.'}, status=405)
    
    

def daily_attendance_page(request):
    dat = timezone.now()
    exect_date = timezone.now().date()
    current_date = dat.strftime("%Y-%m-%d")
    attendance_list = registration.objects.annotate(
        attendance_count=Count(
            'attendance',
            filter=models.Q(
                attendance__date_time__date=current_date,
                attendance__status='IN'
            )
        )
    ).exclude(id=1).values('id', 'name', 'department', 'attendance_count')
    total_users = registration.objects.exclude(id=1).aggregate(count=Count('id'))['count']

    present_count = 0
    absent_count = 0
    presentlist = []
    absentlist = []
    employee_present_list = []
    employee_absent_list = []
    emp_data = []
    ist_tz = pytz.timezone('Asia/Kolkata')  # IST timezone

    for attendance1 in attendance_list:
        attendance_count = attendance1['attendance_count']
        if attendance_count > 0:
            attendance_status = 'Present'
            employee_present_list.append(attendance1['id'])
            present_count += 1
        else:
            attendance_status = 'Absent'
            employee_absent_list.append(attendance1['id'])
            absent_count += 1

    if employee_present_list:
        for i in employee_present_list:
            data = registration.objects.get(id=i)
            id = data.id
            name = data.name
            department = data.department
            statuss = "Present"
            first_in_attendance = attendance.objects.filter(emp_id=i, status='IN', date_time__date=exect_date)
            if first_in_attendance.exists():
                first_in_time_utc = first_in_attendance.earliest('date_time').date_time
                first_in_time_ist = first_in_time_utc.astimezone(ist_tz)
            else:
                first_in_time_ist = "--"

            last_out_attendance = attendance.objects.filter(emp_id=i, status='OUT', date_time__date=exect_date)
            if last_out_attendance.exists():
                last_out_time_utc = last_out_attendance.latest('date_time').date_time
                last_out_time_ist = last_out_time_utc.astimezone(ist_tz)
                time_gap = (last_out_time_utc - first_in_time_utc).total_seconds() / 3600.0
                rounded_time = round(time_gap, 2)
                emp_data.append({
                    "id": id,
                    "name": name,
                    "department": department,
                    "date": exect_date,
                    "first_in": first_in_time_ist.strftime(' %I:%M:%S %p'),
                    "last_out": last_out_time_ist.strftime(' %I:%M:%S %p'),
                    "total": rounded_time,
                    "status": statuss
                })
            else:
                last_out_time_ist = "--"
                rounded_time = "--"
                emp_data.append({
                    "id": id,
                    "name": name,
                    "department": department,
                    "date": exect_date,
                    "first_in": first_in_time_ist.strftime(' %I:%M:%S %p'),
                    "last_out": last_out_time_ist,
                    "total": rounded_time,
                    "status": statuss
                })
    else:
        print("NO one is Present yet")

    if employee_absent_list:
        for i in employee_absent_list:
            data = registration.objects.get(id=i)
            id = data.id
            name = data.name
            department = data.department
            statuss = "Absent"
            attendance_records = attendance.objects.filter(emp_id=i, date_time__date=exect_date)
            if not attendance_records.exists():
                emp_data.append({
                    'id': id,
                    'name': name,
                    'department': department,
                    "date": exect_date,
                    'first_in': '--',
                    'last_out': '--',
                    'total': '--',
                    'status': statuss
                })
    else:
        pass

    emp_data_sorted = sorted(emp_data, key=custom_sort)
    return render(request, "home/daily_attendance_report.html", {"present": present_count,
                                                                 "absent": absent_count, "data": emp_data_sorted})



def custom_sort(entry):
    status_order = {'Present': 0, 'Absent': 1}
    
    if entry['status'] == 'Absent':
        # For absent entries, use a default datetime for sorting
        default_datetime = datetime(1970, 1, 1)  # Using a common starting point
        return status_order['Absent'], default_datetime.timestamp()
    
    # For present entries, parse the 'first_in' attribute
    first_in_str = entry.get('first_in', '00:00:00 AM')
    first_in_datetime = datetime.strptime(first_in_str, ' %I:%M:%S %p')
    
    return status_order['Present'], -first_in_datetime.timestamp()
    


def accept_unknown(request,id):
    unknown_row = get_object_or_404(unknown, id=id)
    id = id
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            emp_id = form.cleaned_data['emp_id']
            date = unknown_row.date_time
            attendance_instance = attendance.objects.create(emp_id=emp_id, status=unknown_row.status, date_time=date, image=unknown_row.image)
            unknown_row.delete()
            return redirect('user:unknow_view')
    else:
        form = AttendanceForm()
    return render(request, 'home/accept_unknown.html', {'form': form, 'unknown_row': unknown_row})


def reject_unknown(request,id):
    unknown_row = get_object_or_404(unknown, id=id)
    rejected_instance = rejected_unknown.objects.create(status=unknown_row.status, date_time=unknown_row.date_time, image=unknown_row.image)
    rejected_data = {
        'rejected_instance': rejected_instance
    }
    unknown_row.delete()
    return redirect('user:unknow_view')


def show_rejected(request):
    rejected = rejected_unknown.objects.all()
    context = {'data': []}
    for item in rejected:
        image_data = item.image 
        image_data_base64 = base64.b64encode(image_data).decode('utf-8')
        context['data'].append({'item': item, 'image_data_base64': image_data_base64})
    return render(request, "home/rejected_detection.html", context)


def delete_rejected(request, id):
    rej = get_object_or_404(rejected_unknown, id=id)
    rej.delete()
    return redirect('user:show_rejected')


def delete_selected_rejects(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('ids[]')
 
        # Delete selected items from unknown model
        unknown_objects = rejected_unknown.objects.filter(id__in=selected_ids)
        unknown_objects.delete()
 
        # Delete corresponding items from rejected_unknown model
        for obj in unknown_objects:
            rejected_instance = rejected_unknown.objects.create(
                status=obj.status,
                date_time=obj.date_time,
                image=obj.image
            )
            rejected_instance.save()
 
        return JsonResponse({'message': 'Items deleted successfully.'})
 
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def fetch_daily_employees(request):
    department = request.GET.get('department')
    if department:
        employees = registration.objects.filter(department=department).values('id', 'name')
        return JsonResponse(list(employees), safe=False)

    return JsonResponse({'error': 'Invalid department'}, status=400)


def check_daily_employee_presence(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        data = json.loads(body)
        employee_ids = data.get('employeeIds', [])
        today = date.today()
        employee_data = []
        present_count = 0
        absent_count = 0
        for emp_id in employee_ids:
            try:
                regdata = registration.objects.get(id=emp_id) 
                has_in_status = attendance.objects.filter(emp_id=emp_id, status='IN', date_time__date=today).exists()
                if has_in_status:
                    status = "Present"
                    first_in_entry = attendance.objects.filter(emp_id=emp_id, status='IN', date_time__date=today).earliest('date_time')
                    first_in_entry_ist = convert_to_ist(first_in_entry.date_time)
                    try:
                        latest_out_entry = attendance.objects.filter(emp_id=emp_id, status='OUT', date_time__date=today).latest('date_time')
                        latest_out_entry_ist = convert_to_ist(latest_out_entry.date_time)
                        time_gap = (latest_out_entry.date_time - first_in_entry.date_time).total_seconds() / 3600.0
                        rounded_time = round(time_gap, 2)
                        employee_data.append({
                            'Emp_ID': emp_id,
                            'Name': regdata.name,
                            'Department': regdata.department,
                            'Date': today,
                            'In_time': format_time(first_in_entry_ist),
                            'Exit_Time': format_time(latest_out_entry_ist),
                            'Total_Hours': rounded_time,
                            'Status': status
                        })
                    except ObjectDoesNotExist:
                        latest_out_entry = "--"
                        latest_out_entry_ist = "--"
                        rounded_time = "--"
                        employee_data.append({
                            'Emp_ID': emp_id,
                            'Name': regdata.name,
                            'Department': regdata.department,
                            'Date': today,
                            'In_time': format_time(first_in_entry_ist),
                            'Exit_Time': format_time(latest_out_entry_ist),
                            'Total_Hours': rounded_time,
                            'Status': status
                        })
                    present_count += 1
                else:
                    status = "Absent"
                    first_in_entry_ist = "--"
                    latest_out_entry_ist = "--"
                    rounded_time = "--"
                    employee_data.append({
                        'Emp_ID': emp_id,
                        'Name': regdata.name,
                        'Department': regdata.department,
                        'Date': today,
                        'In_time': format_time(first_in_entry_ist),
                        'Exit_Time': format_time(latest_out_entry_ist),
                        'Total_Hours': rounded_time,
                        'Status': status
                    })
                    absent_count += 1
            except ObjectDoesNotExist:
                pass

        # Sort employee_data by 'first_in' attribute
        employee_data.sort(key=lambda x: (0 if x['Status'] == 'Present' else 1, x.get('In_time', '')), reverse=True)

        # Separate the 'Present' and 'Absent' entries
        present_entries = [entry for entry in employee_data if entry['Status'] == 'Present']
        absent_entries = [entry for entry in employee_data if entry['Status'] == 'Absent']

        # Combine the lists to have 'Present' entries on top
        employee_data = present_entries + absent_entries        
        context = {
            'employeedata': employee_data,
            'present': present_count,
            'absent': absent_count
        } 
        return JsonResponse(context, safe=False)


def daily_employee_attendance(request):
    if request.method == 'GET':
        emp_id = request.GET.get('employeeId')
        today = date.today()
        employee_data = []
        present_count = 0
        absent_count = 0
        try:
            regdata = registration.objects.get(id=emp_id) 
            has_in_status = attendance.objects.filter(emp_id=emp_id, status='IN', date_time__date=today).exists()
            if has_in_status:
                status = "Present"
                first_in_entry = attendance.objects.filter(emp_id=emp_id, status='IN', date_time__date=today).earliest('date_time')
                try:
                    latest_out_entry = attendance.objects.filter(emp_id=emp_id, status='OUT', date_time__date=today).latest('date_time')
                    time_gap = (latest_out_entry.date_time - first_in_entry.date_time).total_seconds() / 3600.0
                    rounded_time = round(time_gap, 2)
                    employee_data.append({
                        'Emp_ID': emp_id,
                        'Name': regdata.name,
                        'Department': regdata.department,
                        'Date': today,
                        'In_time': first_in_entry.date_time,
                        'Exit_Time': latest_out_entry.date_time,
                        'Total_Hours': rounded_time,
                        'Status': status
                    })
                except ObjectDoesNotExist:
                    latest_out_entry = "--"
                    rounded_time = "--"
                    employee_data.append({
                        'Emp_ID': emp_id,
                        'Name': regdata.name,
                        'Department': regdata.department,
                        'Date': today,
                        'In_time': first_in_entry.date_time,
                        'Exit_Time': latest_out_entry,
                        'Total_Hours': rounded_time,
                        'Status': status
                    })
                present_count += 1
            else:
                status = "Absent"
                first_in_entry = "--"
                latest_out_entry = "--"
                rounded_time = "--"
                employee_data.append({
                    'Emp_ID': emp_id,
                    'Name': regdata.name,
                    'Department': regdata.department,
                    'Date': today,
                    'In_time': first_in_entry,
                    'Exit_Time': latest_out_entry,
                    'Total_Hours': rounded_time,
                    'Status': status
                })
                absent_count += 1
        except ObjectDoesNotExist:
            pass  
        context = {
            'employeedata': employee_data,
            'present': present_count,
            'absent': absent_count
        } 
    return JsonResponse(context, safe=False)


import csv
from django.http import HttpResponse
from django.db.models import Count
from .models import registration, attendance, unknown

# def generate_report(request):
#     # Get current date
#     current_date = date.today()

#     # Query to get total employees
#     total_employees = registration.objects.count()

#     # Query to get present employees for the current date
#     present_employee_ids = attendance.objects.filter(date_time__date=current_date).values_list('emp_id_id', flat=True).distinct()

#     # Query to get employee IDs whose attendance record is empty for the current date
#     all_employee_ids = registration.objects.values_list('id', flat=True)
#     absent_employee_ids = set(all_employee_ids) - set(present_employee_ids)

#     # Query to get total unknown detections for the current date
#     total_unknown_detections = unknown.objects.filter(date_time__date=current_date).count()

#     # Prepare data for CSV
#     report_data = [
#         ['Date', 'Total Employees', 'Present Employees', 'Absent Employees', 'Total Unknown detections', 'Comments'],
#         [current_date, total_employees, len(present_employee_ids), len(absent_employee_ids), total_unknown_detections, 'Add your comments here']
#     ]

#     # Create response object
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="report.csv"'

#     # Write data to CSV
#     writer = csv.writer(response)
#     for row in report_data:
#         writer.writerow(row)

#     return response



from datetime import date, timedelta
import csv

def generate_report(request):
    # Get current date
    current_date = date.today()
    # Assuming you want the report for the current month
    start_date = current_date.replace(day=1)
    end_date = start_date.replace(day=1, month=start_date.month+1)
    end_date -= timedelta(days=1)  # Move to the last day of the current month

    # Get total employees
    total_employees = registration.objects.count()

    # Prepare data for CSV
    report_data = [['Date', 'Total Employees', 'Present Employees', 'Absent Employees', 'Total Unknown detections', 'Comments']]

    # Iterate over each day in the month
    while start_date <= end_date:
        # Query to get present employees for the current date
        present_employee_ids = attendance.objects.filter(date_time__date=start_date).values_list('emp_id_id', flat=True).distinct()

        # Query to get employee IDs whose attendance record is empty for the current date
        all_employee_ids = registration.objects.values_list('id', flat=True)
        absent_employee_ids = set(all_employee_ids) - set(present_employee_ids)

        # Query to get total unknown detections for the current date
        total_unknown_detections = unknown.objects.filter(date_time__date=start_date).count()

        # Check if there is no data available for the current date
        if len(present_employee_ids) == 0 and len(absent_employee_ids) == 0 and total_unknown_detections == 0:
            # If no data available, mark the day as a holiday
            report_data.append([start_date, total_employees, 0, 0, 0, 'Holiday'])
        else:
            # Append data for current date to report_data
            report_data.append([start_date, total_employees, len(present_employee_ids), len(absent_employee_ids), total_unknown_detections, 'Add your comments here'])

        # Move to the next day
        start_date += timedelta(days=1)

    # Create response object
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'

    # Write data to CSV
    writer = csv.writer(response)
    for row in report_data:
        writer.writerow(row)

    return response
