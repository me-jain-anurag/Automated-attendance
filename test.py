from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch

def speak(str1):
    speak=Dispatch(("SAPI.SpVoice"))
    speak.Speak(str1)

def create_ui_frame(frame, info_text="Press 'O' to mark attendance, 'Q' to quit"):
    # Create a larger frame with black background
    height, width = frame.shape[:2]
    ui_frame = np.zeros((height + 100, width + 200, 3), dtype=np.uint8)
    
    # Add main frame
    ui_frame[50:50+height, 100:100+width] = frame
    
    # Add title bar
    cv2.rectangle(ui_frame, (0,0), (ui_frame.shape[1],40), (0,102,204), -1)
    cv2.putText(ui_frame, "Face Recognition Attendance System", (10,30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    
    # Add status bar
    cv2.rectangle(ui_frame, (0,ui_frame.shape[0]-40), (ui_frame.shape[1],ui_frame.shape[0]), (64,64,64), -1)
    cv2.putText(ui_frame, info_text, (10,ui_frame.shape[0]-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1)
    
    # Add border to main frame
    cv2.rectangle(ui_frame, (98,48), (102+width,52+height), (255,255,255), 2)
    
    return ui_frame

video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

with open('data/names.pkl', 'rb') as w:
    LABELS = pickle.load(w)
with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

print('Shape of Faces matrix --> ', FACES.shape)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

COL_NAMES = ['NAME', 'TIME']
attendance_count = 0

while True:
    ret, frame = video.read()
    if not ret:
        break
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    
    for (x,y,w,h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50,50)).flatten().reshape(1,-1)
        output = knn.predict(resized_img)
        
        # Draw face rectangle with gradient effect
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,102,204), 2)
        
        # Add name label with better styling
        label_y = y - 10 if y - 10 > 10 else y + h + 10
        cv2.rectangle(frame, (x-1, label_y-20), (x+w+1, label_y+5), (0,102,204), -1)
        cv2.putText(frame, str(output[0]), (x+5, label_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        
        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
        attendance = [str(output[0]), str(timestamp)]
    
    # Create enhanced UI
    status_text = f"Recognized faces: {len(faces)} | Attendance marked: {attendance_count} | Press 'O' to mark attendance, 'Q' to quit"
    ui_frame = create_ui_frame(frame, status_text)
    
    cv2.imshow("Face Recognition", ui_frame)
    k = cv2.waitKey(1)
    
    if k == ord('o'):
        attendance_count += 1
        speak("Attendance Taken..")
        
        exist = os.path.isfile(f"Attendance/Attendance_{date}.csv")
        with open(f"Attendance/Attendance_{date}.csv", "+a") as csvfile:
            writer = csv.writer(csvfile)
            if not exist:
                writer.writerow(COL_NAMES)
            writer.writerow(attendance)
            
    elif k == ord('q'):
        break

video.release()
cv2.destroyAllWindows()

