import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

DB_PATH = "logs.db"


def initializeDB():
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()

    # create "logs_conversions" table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS logs_conversions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_title TEXT,
            format TEXT,
            timestamp TEXT
        )
    """
    )

    # create "logs_stats" table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS logs_stats (
            id INTEGER PRIMARY KEY,
            total_conversions INTEGER,
            number_of_mp3 INTEGER,
            number_of_mp4 INTEGER
        )
    """
    )

    # put starting value into stats table to initialize it
    cursor.execute("SELECT COUNT(*) FROM logs_stats")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO logs_stats VALUES (1, 0, 0, 0)")

    connect.commit()
    connect.close()


def saveConversion(title, format):
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()

    # get timestamp and format it
    timeStamp = datetime.now().strftime("%d. %B %Y %H:%M:%S")

    # update logs_conversions table
    cursor.execute(
        "INSERT INTO logs_conversions (video_title, format, timestamp) VALUES (?, ?, ?)",
        (title, format, timeStamp),
    )

    # update logs_stats
    if format == "mp3":
        cursor.execute("UPDATE logs_stats SET number_of_mp3 = number_of_mp3 + 1")
    else:
        cursor.execute("UPDATE logs_stats SET number_of_mp4 = number_of_mp4 + 1")

    cursor.execute("UPDATE logs_stats SET total_conversions = total_conversions + 1")

    connect.commit()
    connect.close()


# retrieve all logs
def getLogs():
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM logs_conversions")
    data = cursor.fetchall()

    connect.close()
    return data


# retrieve stats
def getStats():
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM logs_stats WHERE id = 1")
    stats = cursor.fetchone()

    connect.close()
    return stats
