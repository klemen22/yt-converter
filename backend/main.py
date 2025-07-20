from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from yt_dlp import YoutubeDL
from fastapi.responses import FileResponse
import os

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


@app.post("/api/convert")
async def convertVideo(payload: request):
    print("Payload retrieved!", payload)

    ydl_opts = {}

    if payload.format == "mp3":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(downloadDir, "%(title)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "postprocessor_cleanup": True,
        }
    elif payload.format == "mp4":
        resolution = payload.resolution or "best"
        ydl_opts = {
            "format": f"bestvideo[height<={resolution}]+bestaudio/best",
            "outtmpl": os.path.join(downloadDir, "%(title)s.%(ext)s"),
            "merge_output_format": "mp4",
        }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(payload.url, download=True)
            filename = ydl.prepare_filename(info)
            if payload.format == "mp3":
                filename = filename.rsplit(".", 1)[0] + ".mp3"
        return {
            "status": "success",
            "message": "Download complete",
            "filename": os.path.basename(filename),
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
            os.unlink(filePath)
            return {"status": "deleted"}
        else:
            return {"status": "not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
