import sqlite3

#using flask to display the stats on a webpage, rather than just printing them to the console
from flask import Flask, jsonify, render_template, send_from_directory

IMAGE_DIR = "images"

app = Flask(__name__)


def get_stats():
    #A new connection. WAL mode lets this read while main.py writes
    conn = sqlite3.connect("logDB.db")
    try:
        latest = conn.execute(
            "SELECT DATETIME, DISTANCE, PHOTO_PATH FROM VISITS ORDER BY ID DESC LIMIT 1").fetchone()
        total = conn.execute("SELECT COUNT(*) FROM VISITS").fetchone()[0]
        today = conn.execute(
            "SELECT COUNT(*) FROM VISITS WHERE DATE(DATETIME) = DATE('now', 'localtime')").fetchone()[0]
        days = conn.execute("SELECT COUNT(DISTINCT DATE(DATETIME)) FROM VISITS").fetchone()[0]
        busiest = conn.execute(
            "SELECT STRFTIME('%H', DATETIME) AS HOUR FROM VISITS "
            "GROUP BY HOUR ORDER BY COUNT(*) DESC LIMIT 1").fetchone()
        detection_range = conn.execute(
            "SELECT DETECTION_RANGE FROM STATUS WHERE ID = 1").fetchone()
    finally:
        conn.close()

 
    #It will display None for the stats that don't exist yet so it doesn't crash the webpage if the DB is empty.
    return {
        "latest": None if latest is None else {
            "time": latest[0],
            "distance": latest[1],
            "photo": "/" + latest[2],
        },
        "visitsToday": today,
        "totalVisits": total,
        "averagePerDay": round(total / days, 1) if days else None, #Averaged over days that had visits
        "busiestHour": None if busiest is None else int(busiest[0]),
        "detectionRange": None if detection_range is None else detection_range[0],
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stats")
def stats():
    return jsonify(get_stats())


@app.route("/images/<path:filename>")
def images(filename):
    return send_from_directory(IMAGE_DIR, filename)


if __name__ == "__main__":
    #Just a random port, since this is only for local network use. The port can be changed if needed.
    app.run(host="0.0.0.0", port=5000)