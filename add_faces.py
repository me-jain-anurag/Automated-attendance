import cv2
import numpy as np
from data_handler import DataHandler

def collect_face_data():
    # Initialize video capture and face detector
    video = cv2.VideoCapture(0)
    facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
    data_handler = DataHandler()
    
    faces_data = []
    i = 0
    
    # Get user name with validation
    while True:
        name = input("Enter Your Name (minimum 2 characters): ").strip()
        if len(name) >= 2:
            break
        print("Name too short, please try again")
    
    print(f"Collecting face data for {name}. Press 'q' to quit early.")
    print("Please move your face slightly to capture different angles.")
    
    while True:
        ret, frame = video.read()
        if not ret:
            print("Error: Could not access camera")
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facedetect.detectMultiScale(gray, 1.3, 5)
        
        for (x,y,w,h) in faces:
            crop_img = frame[y:y+h, x:x+w, :]
            resized_img = cv2.resize(crop_img, (50,50))
            
            if len(faces_data)<=100 and i%10==0:
                faces_data.append(resized_img)
                
            i = i+1
            
            # Draw feedback
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(frame, f"Samples: {len(faces_data)}/100", (10,30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            
        cv2.imshow("Face Registration", frame)
        
        # Break if 'q' pressed or enough samples collected
        if cv2.waitKey(1)==ord('q') or len(faces_data)==100:
            break
    
    video.release()
    cv2.destroyAllWindows()
    
    if len(faces_data) < 20:
        print("Not enough face data collected. Please try again.")
        return
    
    # Process and save face data
    faces_data = np.asarray(faces_data)
    faces_data = faces_data.reshape(len(faces_data), -1)
    
    if data_handler.save_data(name, faces_data):
        print(f"Successfully registered {name}!")
    else:
        print("Error saving face data. Please try again.")

if __name__ == "__main__":
    collect_face_data()