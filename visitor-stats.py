import sqlite3
from datetime import datetime


def load_visits():
    conn = sqlite3.connect('logDB.db')
    c = conn.cursor()
    c.execute("SELECT * FROM VISITS")
    visits = c.fetchall()
    conn.close()
    return visits


def main():
    visits = load_visits()
    print(f"Total visits: {len(visits)}")
    
    for visit in visits:
        print(f"ID: {visit[0]}, DATETIME: {visit[1]}, DISTANCE: {visit[2]}, PHOTO_PATH: {visit[3]}, FACE_DETECTED: {visit[4]}")
    
    print("Average distance: {:.2f} cm".format(sum(visit[2] for visit in visits) / len(visits)) if visits else 0)
    print("Average visit per day: {:.2f}".format(len(visits) / len(set(visit[1].split('T')[0] for visit in visits))) if visits else 0)
    