import sqlite3
import os
from datetime import datetime


def load_visits():
    conn = sqlite3.connect('logDB.db')
    c = conn.cursor()
    c.execute("SELECT * FROM VISITS")
    visits = c.fetchall()
    conn.close()
    return visits

def clear_console():
    os.system('clear')


def main():
    visits = load_visits()
    
    for visit in visits:
        print(f"ID: {visit[0]}, DATETIME: {visit[1]}, DISTANCE: {visit[2]}, PHOTO_PATH: {visit[3]}")
    
    print(f"Total visits: {len(visits)}")    
    print("Average distance: {:.2f} cm".format(sum(visit[2] for visit in visits) / len(visits)) if visits else 0)
    print("Average visit per day: {:.2f}".format(len(visits) / len(set(visit[1].split('T')[0] for visit in visits))) if visits else 0)
    
    while True:
        clear_console()
        visits = load_visits()
        time.sleep(5)  # Refresh every 5 seconds
    
    
if __name__ == "__main__":
    main()