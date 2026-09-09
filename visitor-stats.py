import sqlite3
from datetime import datetime


def load_visits():
    conn = sqlite3.connect('logDB.db')
    c = conn.cursor()
    c.execute("SELECT * FROM VISITS")
    visits = c.fetchall()
    conn.close()
    return visits

def average_distance():
    conn = sqlite3.connect('logDB.db')
    c = conn.cursor()
    c.execute("SELECT AVG(DISTANCE) FROM VISITS")
    avg_distance = c.fetchone()[0]
    conn.close()
    return avg_distance

for visit in load_visits():
    print(visit)
    
for distance in average_distance():
    print(f"Average distance: {distance} cm")