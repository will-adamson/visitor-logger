import serial
import sqlite3
import cv2 as cv
from datetime import datetime

arduino = serial.Serial(port='COM10',  baudrate=9600, timeout=.1)
conn = sqlite3.connect('logDB.db')
c = conn.cursor()

try:
    c.execute('''CREATE TABLE IF NOT EXISTS VISITS
                 (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  DISTANCE REAL,
                  PHOTO_PATH TEXT,
                  DETECTED INTEGER)''')
    while True:
        data = arduino.readline().decode('utf-8').strip()
        if data:
            print(data)
            row = data.split(',')
            if len(row) == 2:
                event_type = row[0]
                distance = int(row[1])
                timestamp = datetime.now().isoformat(timespec="seconds")
                #Both of the following lines are placeholders for once I have photo taking and image detection working
                face_detected = 1
                photo_path = "/test.jpg"

                c.execute("INSERT INTO VISITS (datetime, distance, photo_path, face_detected) VALUES (?, ?, ?, ?)",
                        (timestamp, distance, photo_path, face_detected))
                conn.commit()
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    arduino.close()
    conn.close()
            