import tkinter as tk
import yt_dlp
import os
from mutagen.easyid3 import EasyID3
import sys
import threading
from win32com.shell import shell, shellcon


root = tk.Tk()
root.geometry('500x600')
root.resizable(0,0)
root.title("DownTube - Youtube Downloader")
root.configure(bg='black')

tk.Label(root,text = 'Youtube Video Downloader', font ='arial 20 bold', background = 'black', fg = 'white').pack()

link = tk.StringVar()

tk.Label(root, text = 'Paste Link Here:', font = 'arial 15 bold', background = 'black', fg = 'white', bd = 2).place(x= 160 , y = 60)
link_enter = tk.Entry(root, width = 70,textvariable = link, background = 'black', fg = 'white').place(x = 32, y = 90)

if os.name == 'nt':
    musicDir = shell.SHGetKnownFolderPath(shellcon.FOLDERID_Music, 0, 0)
elif os.name == 'posix':
    musicDir = os.path.expanduser('~/Music')

class PrintLogger(): # create file like object
    def __init__(self, textbox): # pass reference to text widget
        self.textbox = textbox # keep ref

    def write(self, text):
        self.textbox.insert(tk.END, text) # write text to textbox
        self.textbox.see(tk.END)    # could also scroll to end of textbox here to make sure always visible

    def flush(self): # needed for file like object
        pass
t = tk.Text(root, height = 10, width = 70, background = 'black', fg = 'white',  wrap='word')
t.place(x = 500, y = 1000)
t.pack(side="right", fill="x", expand=True)
# create instance of file like object
pl = PrintLogger(t)

# replace sys.stdout with our object
sys.stdout = pl

x = threading.Thread(target=PrintLogger, args=(1,))
x.start()
def Downloader():     
    url = str(link.get())
    print('Dowloading: '+url+'\n')
    video_info = yt_dlp.YoutubeDL().extract_info(url = url,download=False)
    year = video_info['upload_date']
    filename = fr"{video_info['title']}.mp3"
    #print(filename)
    newFilename = list(filename)
    for i in range (0, len(newFilename)):
        if newFilename[i] == '|':
            newFilename[i] = '#'
    filename = ''.join(newFilename)
    #print(filename)
    filePath = musicDir+"/Downloaded/" + filename
    #filenametmp = r"W:\Muzyka z YT\temp filename for the song.mp3"
    options={'format':'bestaudio/best', 'keepvideo':False, 'outtmpl':filePath, 'addmetadata':True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        },
        {
            'key': 'FFmpegMetadata', 
        }
        ]}

    yt_dlp.YoutubeDL(options).download([video_info['webpage_url']])
    
    #os.rename(filenametmp, filename)

    #tk.Label(root, text = 'Adding metadata', font = 'arial 15', background = 'black', fg = 'white').place(x= 50 , y = 210)
    metatag = EasyID3(filePath)
    metatag['title'] = video_info['title']
    metatag['artist'] = "Unknown"
    metatag['date'] = year[0:4]
    metatag.RegisterTextKey("track", "TRCK")
    metatag['track'] = ''
    metatag.save()
    print('\n Finished!\n')
    tk.Label(root, text = 'DOWNLOADED', font = 'arial 15', background = 'black', fg = 'white').place(x= 180 , y = 450)  
    tk.Label(root, text = f"{video_info['title']}", font = 'arial 15', background = 'black', fg = 'white').place(x= 32 , y = 500)
def DownloaderStart(event=None):
    y = threading.Thread(target=Downloader)
    y.start()
butt = tk.Button(root,text = 'DOWNLOAD', font = 'arial 15 bold' ,bg = 'dark blue', padx = 2, command = DownloaderStart)
butt.place(x=180 ,y = 150)
root.bind('<Return>', DownloaderStart)
root.mainloop()

###TODO:Wyciągnij path do folderu Muzyka i tam wrzucaj dynamicznie pliki