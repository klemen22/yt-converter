
from yt_dlp import YoutubeDL
def download_video(link):
    ydl_opts = {}
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

link = input("Vnesi YouTube povezavo: ")
download_video(link)
