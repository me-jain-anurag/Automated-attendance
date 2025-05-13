import cv2
import pickle
import numpy as np
import os

# Initialize video capture and face detector
video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

faces_data = []
i = 0

name = input("Enter Your Name: ")

# Capture face data
while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50,50))
        if len(faces_data)<=100 and i%10==0:
            faces_data.append(resized_img)
        i = i+1
        cv2.putText(frame, str(len(faces_data)), (50,50), cv2.FONT_HERSHEY_COMPLEX, 1, (50,50,255), 1)
        cv2.rectangle(frame, (x,y), (x+w, y+h), (50,50,255), 1)
    cv2.imshow("Frame",frame)
    k = cv2.waitKey(1)
    if k==ord('q') or len(faces_data)==100:
        break

video.release()
cv2.destroyAllWindows()

# Process and save face data
faces_data = np.asarray(faces_data)
faces_data = faces_data.reshape(100, -1)
names = [name]*100

# Save the current face data (overwrite existing data)
with open('data/faces_data.pkl', 'wb') as f:
    pickle.dump(faces_data, f)

# Save the current names (overwrite existing data)
with open('data/names.pkl', 'wb') as f:
    pickle.dump(names, f)

print(f"Face data saved for {name}. You can now run test.py to start recognition.")