import sqlite3
import os
import time
from datetime import datetime


def load_visits():
    conn = sqlite3.connect('logDB.db')
    c = conn.cursor()
    c.execute("SELECT * FROM VISITS")
    visits = c.fetchall()
    conn.close()
    return visits

def print_visits(visits):
    for visit in visits:
            print(f"ID: {visit[0]}, DATETIME: {visit[1]}, DISTANCE: {visit[2]}, PHOTO_PATH: {visit[3]}")
    #BEGIN: Code completion
    #VSCode auto completed my print statments as I wrote them, it did what I was planning on writing anyway.
    #Seemed pointless to try rewrite them another way that was "mine". 
    print(f"Total visits: {len(visits)}")    
    print("Average distance: {:.2f} cm".format(sum(visit[2] for visit in visits) / len(visits)) if visits else 0)
    print("Average visit per day: {}".format(len(visits) / len(set(visit[1].split('T')[0] for visit in visits))) if visits else 0)
    #END: Code completion

def clear_console():
    os.system('clear')


def main():
    visits = load_visits()

    while True:
        clear_console()
        print_visits(visits)
        time.sleep(5)  # Refresh every 5 seconds
    
    
if __name__ == "__main__":
    main()