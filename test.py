from sklearn.neighbors import KNeighborsClassifier
import cv2
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch
from data_handler import DataHandler

def speak(str1):
    speak = Dispatch(("SAPI.SpVoice"))
    speak.Speak(str1)

# Initialize components
video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
data_handler = DataHandler()

# Load face data
print("Loading face recognition data...")
FACES, LABELS = data_handler.load_data()

if FACES is None or LABELS is None:
    print("Error: Could not load face data. Please add face data first using add_faces.py")
    video.release()
    cv2.destroyAllWindows()
    exit(1)

print('Shape of Faces matrix --> ', FACES.shape)
print(f'Number of people in database: {len(set(LABELS))}')

# Initialize and train KNN classifier
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

# Create Attendance directory if needed
if not os.path.exists("Attendance"):
    os.makedirs("Attendance")

print("\nFace recognition started. Press 'o' to mark attendance, 'q' to quit.")

while True:
    ret, frame = video.read()
    if not ret:
        print("Error: Could not access camera")
        break
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    
    for (x,y,w,h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50,50)).flatten().reshape(1,-1)
        output = knn.predict(resized_img)
        
        # Get current timestamp
        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
        
        # Draw face detection and name
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
        cv2.putText(frame, str(output[0]), (x,y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
        
        attendance = [str(output[0]), str(timestamp)]
        
    cv2.putText(frame, "Press 'o' to mark attendance", (10, frame.shape[0]-20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    cv2.imshow("Face Recognition", frame)
    
    k = cv2.waitKey(1)
    if k == ord('o'):
        try:
            attendance_file = f"Attendance/Attendance_{date}.csv"
            file_exists = os.path.isfile(attendance_file)
            
            with open(attendance_file, "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(['NAME', 'TIME'])
                writer.writerow(attendance)
            
            speak("Attendance Taken")
            print(f"Marked attendance for {attendance[0]} at {attendance[1]}")
            
        except Exception as e:
            print(f"Error marking attendance: {str(e)}")
            
    elif k == ord('q'):
        break

video.release()
cv2.destroyAllWindows()

