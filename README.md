# YTDownloader
Simple GUI interface for yt-dlp made using Tkinter (v1) and  PyQt5 (v2).

Default settings right now are to download an mp3 file with sample matetags to the folder "Downloaded" in user's Music folder disregarding where it may be. You can change that folder since version 2.1
 
App works without issues on Windows, has trouble on Linux where it only works using Wine and is untested on MacOS. On Linux you can run the python file directly if you have all the dependencies installed and compile it using pyinstaller but it will crash upon downloading the first file. Also if you run it with Wine it will fall back to a basic font unless you have some version of Segoe UI font installed for it. 

If you want to edit it you will need yt_dlp and PyQt5/Tkinter. To compile it into an .exe file you can use pyinstaller library with at least --onefile and --noconsole arguments as well as --add-binary for ffmpeg. 
