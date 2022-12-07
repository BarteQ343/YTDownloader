import tkinter as tk
import yt_dlp
import os
from mutagen.easyid3 import EasyID3
import sys
import threading
from win32com.shell import shell, shellcon
import tkinter.font as font

root = tk.Tk()
root.geometry('500x600')
root.resizable(0,0)
root.title("DownTube - Youtube Downloader")
root.configure(bg='black')

cwd = os.getcwd()

tk.Label(root,text = '', font ='arial 20 bold', background = 'black', fg = 'white').pack()
tk.Label(root,text = 'Youtube Video Downloader', font ='arial 20 bold', background = 'black', fg = 'white').pack()

link = tk.StringVar()

bg = str(cwd)+'\\assets\\linkInsert.png'
ph = tk.PhotoImage(file=bg)
back = tk.Label(root,image=ph)
back.image = ph
back.place(x = 37, y = 155)
tk.Label(root, text = 'Paste Link Here:', font = 'arial 15 bold', background = 'black', fg = 'white', bd = 2).place(x= 170 , y = 120)
link_enter = tk.Entry(root, width = 58,textvariable = link, fg = 'white', borderwidth=0, background='#555555',font='arial 10').place(x = 47, y = 158)

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
t = tk.Text(root, height = 7, width = 55, background = 'black', fg = 'white',  wrap='word',)
t.place(x = 32, y = 1060)
t.pack(side="right", expand=True)
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
    newFilename = list(filename)
    for i in range (0, len(newFilename)):
        if newFilename[i] == '|' and newFilename[i] == '"' and newFilename[i] == '?':
            newFilename[i] = '#'
    filename = ''.join(newFilename)
    filePath = musicDir+"/Downloaded/" + filename
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


bg = str(cwd)+'\\assets\\button.png'
bgh = str(cwd)+'\\assets\\buttonHover.png'
ph = tk.PhotoImage(file=bg)
phh = tk.PhotoImage(file=bgh)

def on_enter(e):
    butt['image'] = phh

def on_leave(e):
    butt['image'] = ph

butt = tk.Button(root, image = ph, width = 152, height = 50,borderwidth = 0, command = DownloaderStart)
butt.image = ph
butt.place(x=174 ,y = 210)
butt.bind("<Enter>", on_enter)
butt.bind("<Leave>", on_leave)
root.bind('<Return>', DownloaderStart)
root.mainloop()
