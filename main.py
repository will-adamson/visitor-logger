import serial
import sqlite3
import cv2 as cv
from datetime import datetime

def take_photo():
    #todo: replace with picamera2 functionality
    return "/test.jpg"

raw_image = take_photo()

def detect_face(raw_image):
    #BEGIN: https://www.datacamp.com/tutorial/face-detection-python-opencv
    #The following code is from a tutorial on face detection using OpenCV. 
    # I will still need to change it up for my own use case.
    
    img = cv.imread(raw_image)
    gray_image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    face_classifier = cv.CascadeClassifier(
    cv.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    face = face_classifier.detectMultiScale(
    gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
    #END: https://www.datacamp.com/tutorial/face-detection-python-opencv
    
    return 1 if len(face) > 0 else 0

arduino = serial.Serial(port='COM10',  baudrate=9600, timeout=.1)
conn = sqlite3.connect('logDB.db')
c = conn.cursor()

try:
    c.execute('''CREATE TABLE IF NOT EXISTS VISITS
                (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                DATETIME TEXT,
                DISTANCE REAL,
                PHOTO_PATH TEXT,
                FACE_DETECTED INTEGER)''')
    while True:
        data = arduino.readline().decode('utf-8').strip()
        
        if data:
            print(data) #For testing
            row = data.split(',')
            
            if len(row) == 2: #As long as there is a distamce, proceed
                distance = int(row[1])
                photo_path = take_photo()
                face_detected = detect_face(photo_path)
                
                if (face_detected == 1):
                    timestamp = datetime.now().isoformat(timespec="seconds")
                    c.execute("INSERT INTO VISITS (datetime, distance, photo_path, face_detected) VALUES (?, ?, ?, ?)",
                            (timestamp, distance, photo_path, face_detected))
                    conn.commit()
                    print(f"Face detected at {timestamp}. Distance: {distance} cm. Photo saved at {photo_path}.")
                else:
                    print(f"No face detected. Distance: {distance} cm. Photo deleted.")
                    
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    arduino.close()
    conn.close()
            