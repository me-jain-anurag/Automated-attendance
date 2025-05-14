# test.py
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch
from sklearn.neighbors import KNeighborsClassifier

def speak(str1):
    speak = Dispatch("SAPI.SpVoice")
    speak.Speak(str1)

def create_ui_frame(frame, info_text="Press 'O' to mark attendance, 'Q' to quit"):
    height, width = frame.shape[:2]
    ui_frame = np.zeros((height + 100, width + 200, 3), dtype=np.uint8)
    ui_frame[50:50+height, 100:100+width] = frame
    cv2.rectangle(ui_frame, (0,0), (ui_frame.shape[1],40), (0,102,204), -1)
    cv2.putText(ui_frame, "Face Recognition Attendance System", (10,30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    cv2.rectangle(ui_frame, (0,ui_frame.shape[0]-40), (ui_frame.shape[1],ui_frame.shape[0]), (64,64,64), -1)
    cv2.putText(ui_frame, info_text, (10,ui_frame.shape[0]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1)
    cv2.rectangle(ui_frame, (98,48), (102+width,52+height), (255,255,255), 2)
    return ui_frame

video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

with open('data/names.pkl', 'rb') as w:
    LABELS = pickle.load(w)
with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

COL_NAMES = ['NAME', 'TIME']
attendance_count = 0
already_marked = set()

while True:
    ret, frame = video.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    recognized_names = []

    for (x,y,w,h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50,50)).flatten().reshape(1,-1)
        output = knn.predict(resized_img)[0]
        recognized_names.append(output)

        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,102,204), 2)
        label_y = y - 10 if y - 10 > 10 else y + h + 10
        cv2.rectangle(frame, (x-1, label_y-20), (x+w+1, label_y+5), (0,102,204), -1)
        cv2.putText(frame, output, (x+5, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
        attendance = [output, timestamp]

    ui_frame = create_ui_frame(frame, f"Recognized: {len(faces)} | Attendance marked: {attendance_count} | O: Mark, Q: Quit")
    cv2.imshow("Face Recognition", ui_frame)
    k = cv2.waitKey(1)

    if k == ord('o'):
        for name in recognized_names:
            if name not in already_marked:
                already_marked.add(name)
                attendance_count += 1
                speak("Attendance Taken.")
                filename = f"Attendance/Attendance_{date}.csv"
                file_exists = os.path.isfile(filename)
                with open(filename, "+a", newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    if not file_exists:
                        writer.writerow(COL_NAMES)
                    writer.writerow([name, timestamp])

    elif k == ord('q'):
        break

video.release()
cv2.destroyAllWindows()