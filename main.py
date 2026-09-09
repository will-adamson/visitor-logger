import serial
import sqlite3
import cv2 as cv
import os
import time
from picamera2 import Picamera2
from datetime import datetime

#BEGIN: https://randomnerdtutorials.com/raspberry-pi-picamera2-python/
#Pretty heavily altered to fit my use case
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()
time.sleep(2)
os.makedirs("images", exist_ok=True)

def take_photo():

    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    photo_path = f"images/{timestamp}.jpg"
    picam2.capture_file(photo_path)

    return photo_path
    #END: https://randomnerdtutorials.com/raspberry-pi-picamera2-python/
    

def detect_face(raw_image):
    #BEGIN: https://www.datacamp.com/tutorial/face-detection-python-opencv
    #The following code is from a tutorial on face detection using OpenCV. 
    # I slightly changed it for my own use case.
    
    img = cv.imread(raw_image)
    gray_image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    face_classifier = cv.CascadeClassifier(
    cv.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    face = face_classifier.detectMultiScale(
    gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
    #END: https://www.datacamp.com/tutorial/face-detection-python-opencv
    
    return 1 if len(face) > 0 else 0

arduino = serial.Serial(port='/dev/ttyACM0',  baudrate=9600, timeout=.1)
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
                    os.remove(photo_path)
                    print(f"No face detected. Distance: {distance} cm. Photo deleted.")
                    
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    picam2.stop()
    arduino.close()
    conn.close()
            