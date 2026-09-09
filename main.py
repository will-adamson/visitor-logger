import serial
import time
import sqlite3

arduino = serial.Serial(port='COM10',  baudrate=9600, timeout=.1)


while True:
    line = arduino.readline().decode('utf-8').strip()
    if line:
        print(line)