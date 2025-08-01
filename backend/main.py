# -------------------------------------------------------------------------------------------#
#                                         Imports                                            #
# -------------------------------------------------------------------------------------------#

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from yt_dlp import YoutubeDL
from fastapi.responses import FileResponse
import os
import re
import threading
import time
import hashlib
import random
from database import initializeDB, saveConversion, getLogs, getStats

initializeDB()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

downloadDir = "downloads"
if os.path.exists(downloadDir) == False:
    os.mkdir(downloadDir, exist_ok=True)


class request(BaseModel):
    url: str
    format: str
    resolution: str | None = None


# -------------------------------------------------------------------------------------------#
#                                         API calls                                          #
# -------------------------------------------------------------------------------------------#


@app.post("/api/convert")
async def convertVideo(payload: request):
    print("Payload retrieved!", payload)

    uniqueHash = generateHash()
    ydl_opts = {}

    if payload.format == "mp3":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(downloadDir, f"%(title)s_{uniqueHash}.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "postprocessor_cleanup": True,
            "no_cookies_from_browser": True,
            "rm_cache_dir": True,
            "no_cache_dir": True,
            "cachedir": False,
            "nopart": True,
            "noplaylist": True,
        }

    elif payload.format == "mp4":
        resolution = payload.resolution or "best"
        ydl_opts = {
            "format": f"bestvideo[height<={resolution}]+bestaudio/best",
            "outtmpl": os.path.join(downloadDir, f"%(title)s_{uniqueHash}.%(ext)s"),
            "merge_output_format": "mp4",
            "postprocessor_cleanup": True,
            "no_cookies_from_browser": True,
            "rm_cache_dir": True,
            "no_cache_dir": True,
            "cachedir": False,
            "nopart": True,
            "noplaylist": True,
        }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(payload.url, download=True)
            filename = ydl.prepare_filename(info)
            if filename is None:
                raise ValueError("Filename could not be determined.")
            if payload.format == "mp3":
                filename = filename.rsplit(".", 1)[0] + ".mp3"
            cleanName = os.path.basename(filename)
            saveConversion(cleanName, payload.format)
        return {
            "status": "success",
            "message": "Download complete",
            "filename": cleanName,
        }
    except Exception as e:
        print("Error while downloading: ", e)
        return {"status": "error", "message": str(e)}


@app.get("/api/download/{filename}")
def downloadFile(filename: str):
    filePath = os.path.join(downloadDir, filename)
    if os.path.exists(filePath):
        return FileResponse(
            path=filePath, filename=filename, media_type="application/octet-stream"
        )
    else:
        return {"status": "error", "message": "File not found"}


@app.delete("/api/delete/{filename}")
async def deleteFile(filename: str):
    filePath = os.path.join(downloadDir, filename)
    try:
        if os.path.exists(filePath):
            os.remove(filePath)
            return {"status": "deleted"}
        else:
            return {"status": "not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/logs")
def downloadLogs():
    try:
        logs = getLogs()
        logsFilePath = "downloads/logs.txt"
        with open(logsFilePath, "w", encoding="utf-8") as temp:
            for row in logs:
                temp.write(f"{row}\n")
        return FileResponse(
            path=logsFilePath, filename="logs.txt", media_type="text/plain"
        )
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/stats")
def downloadStats():
    try:
        stats = getStats()
        return {
            "status": "success",
            "total_conversions": stats[1],
            "number_of_mp3": stats[2],
            "number_of_mp4": stats[3],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# -------------------------------------------------------------------------------------------#
#                                    Garbage collector                                       #
# -------------------------------------------------------------------------------------------#


def deleteGarbage():
    # on set interval delete all files / leftovers in downloads folder

    while True:
        startInt = time.time()
        endInt = startInt - 30 * 60

        filesList = os.listdir(downloadDir)

        for file in filesList:
            filePath = os.path.join(downloadDir, file)
            if os.path.isfile(filePath):
                if os.path.getatime(filePath) < endInt:
                    try:
                        os.remove(filePath)
                        print(f"Deleted old file: {file}")
                    except Exception as e:
                        print(f"Error deleting {file}: {e}")

        time.sleep(600)


# start new thread
threading.Thread(target=deleteGarbage, daemon=True).start()


# -------------------------------------------------------------------------------------------#
#                                     Helper functions                                       #
# -------------------------------------------------------------------------------------------#


def generateHash():
    uniqueHash = hashlib.sha1(str(random.random()).encode()).hexdigest()[:8]
    return uniqueHash
