# YTDownloader
Simple GUI interface for yt-dlp made using Tkinter (v1) and  PyQt5 (v2).

Default settings right now are to download an mp3 file with sample matetags to the folder "Downloaded" in user's Music folder disregarding where it may be.
 
App works without issues on Windows, has trouble adding metatags on Linux where it only works using Wine and is untested on MacOS.

If you want to edit it you will need yt_dlp and PyQt5/Tkinter. To compile it into an .exe file you can use pyinstaller library with at least --onefile argument. 
