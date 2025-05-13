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

# Process new face data
faces_data = np.asarray(faces_data)
faces_data = faces_data.reshape(100, -1)
new_names = [name]*100

# Load existing data if available
existing_faces = []
existing_names = []
if os.path.exists('data/faces_data.pkl'):
    with open('data/faces_data.pkl', 'rb') as f:
        existing_faces = pickle.load(f)
if os.path.exists('data/names.pkl'):
    with open('data/names.pkl', 'rb') as f:
        existing_names = pickle.load(f)

# Combine existing and new data
if len(existing_faces) > 0:
    combined_faces = np.vstack((existing_faces, faces_data))
    combined_names = existing_names + new_names
else:
    combined_faces = faces_data
    combined_names = new_names

# Save combined face data
with open('data/faces_data.pkl', 'wb') as f:
    pickle.dump(combined_faces, f)

# Save combined names
with open('data/names.pkl', 'wb') as f:
    pickle.dump(combined_names, f)

print(f"Face data saved for {name}. Total people in database: {len(set(combined_names))//100}")