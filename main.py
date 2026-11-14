import os
import sqlite3
import time
from datetime import datetime

import cv2 as cv
import serial
from picamera2 import Picamera2

IMAGE_DIR = "images"

#Loaded once at startup instead of on every photo
FACE_CLASSIFIER = cv.CascadeClassifier(
    cv.data.haarcascades + "haarcascade_frontalface_default.xml")

#CascadeClassifier doesn't raise if the file is missing, it just never finds faces
if FACE_CLASSIFIER.empty():
    raise RuntimeError("Failed to load Haar cascade file")

def setup_camera():
    #BEGIN: https://randomnerdtutorials.com/raspberry-pi-picamera2-python/
    #Picam set up, altered to fit my use case (image size restraints, moved into its own function)
    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    time.sleep(2)
    #END: https://randomnerdtutorials.com/raspberry-pi-picamera2-python/
    return picam2


def setup_db():
    #Setup database in its own function, rather than in main loop.
    conn = sqlite3.connect("logDB.db")
    conn.execute("PRAGMA journal_mode=WAL;") #For easier displaying of the info while running the program
    conn.execute('''CREATE TABLE IF NOT EXISTS VISITS
                    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    DATETIME TEXT,
                    DISTANCE REAL,
                    PHOTO_PATH TEXT)''')
    
    return conn

def take_photo(picam2, now):
    photo_path = f"{IMAGE_DIR}/{now.strftime('%Y%m%d_%H%M%S')}.jpg"
    picam2.capture_file(photo_path)
    
    return photo_path

    

def detect_face(photo_path):
    img = cv.imread(photo_path)
    if img is None: #imread returns None if there's no file
        raise RuntimeError(f"Could not read photo: {photo_path}")

    #BEGIN: https://www.datacamp.com/tutorial/face-detection-python-opencv
    #The following code is from a tutorial on face detection using OpenCV.
    #I slightly changed it for my own use case, and only took what was needed for my program
    gray_image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    faces = FACE_CLASSIFIER.detectMultiScale(
        gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
    #END: https://www.datacamp.com/tutorial/face-detection-python-opencv
    return len(faces) > 0

def parse_line(line):
    #Arduino output format: "DETECTED,<distance>" or "RANGE,<range>"
    parts = line.split(",")
    if len(parts) != 2 or parts[0] not in ("DETECTED", "RANGE"):
        print(f"Ignoring unexpected serial line: {line!r}")
        return None, None
    return parts[0], int(parts[1])

def handle_detection(picam2, conn, distance):
    #Detection and DB insert
    now = datetime.now() #One timestamp shared by the photo and the DB row
    photo_path = take_photo(picam2, now)

    if detect_face(photo_path):
        conn.execute("INSERT INTO VISITS (DATETIME, DISTANCE, PHOTO_PATH) VALUES (?, ?, ?)",
                     (now.isoformat(timespec="seconds"), distance, photo_path))
        conn.commit()
        print(f"Face detected at {now:%H:%M:%S}. Distance: {distance} cm. Saved {photo_path}.")
    else:
        os.remove(photo_path)
        print(f"No face detected. Distance: {distance} cm. Photo deleted.")
        
def main():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    picam2 = setup_camera()
    arduino = serial.Serial(port="/dev/ttyACM0", baudrate=9600, timeout=0.1)
    conn = setup_db()

    try:
        while True:
            #The Arduino resets when the port opens, so early bytes can be garbage
            line = arduino.readline().decode("utf-8", errors="replace").strip()
            if not line:
                continue
            message, value = parse_line(line)
            if message == "DETECTED":
                handle_detection(picam2, conn, value)
            elif message == "RANGE":
                print(f"Detection range set to {value} cm")
    finally:
        picam2.stop()
        arduino.close()
        conn.close()


if __name__ == "__main__":
    main()