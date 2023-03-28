from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QScrollBar  # all the PyQt5 are for visual side of things
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtGui import QColor, QTextCursor
import yt_dlp                               # for Downloading from YouTube
import os                                   # for getting os type (Win or Linux)
from mutagen.easyid3 import EasyID3         # for adding sample metadata
import sys                                  # for saving file
import threading                            # for real time console in tkinter
from win32com.shell import shell, shellcon  # for finding out where the music library is #type: ignore               
from yt_dlp.utils import DownloadError      # for error handling (duh)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))   # getting workfolder path for locating assets

if os.name == 'nt':                                                                 # checking if its Windows or Linux (or Mac but can't test it)
    musicDir = shell.SHGetKnownFolderPath(shellcon.FOLDERID_Music, 0, 0)    
elif os.name == 'posix':                                                            # also I'm doing nothing with linux yet as PyQt seems to dislike it. It works semi-fine with Wine only failing to tag the files which might be a problem but I'll cross that bridge when I get to it
    musicDir = os.path.expanduser('~/Music')

# create file-like object
class PrintLogger:
    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, message):
        self.text_edit.insertPlainText(message)
        self.text_edit.moveCursor(QTextCursor.End)
        self.text_edit.ensureCursorVisible()

    def flush(self):
        pass

# create fake logger for exception handling
class LoggerOutputs:
    def error(self, msg):
        print("Captured Error")

    def warning(self, msg):
        print("Captured Warning")

    def debug(self, msg):
        Log=0      

class Window(QWidget):
    def __init__(self):
        super().__init__()

        # set window properties
        self.setWindowTitle("YT downloader")
        self.setGeometry(100, 100, 570, 600)

        # set Material You design stylesheet with changes
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #FFFFFF;
                font-family: Segoe UI, sans-serif;
                font-size: 14px;
            }
            QLabel {
                font-size: 32px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #1F1F1F;
                color: #FFFFFF;
                border-radius: 10px;
                border: none;
                padding: 8px;
            }
            QPushButton {
                background-color: #3800A3;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 8px 16px;
                font-weight: bold;
                font-size:20px;
            }
            QPushButton:hover {
                background-color: #0004FF;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 8px 16px;
                font-weight: bold;
                font-size:20px;
            }
            QPushButton:pressed {
                background-color: #3800A3;
                color: #FFFFFF;
                border-radius: 20px;
                padding: 5px 14px;
                font-weight: bold;
                font-size:20px;
            }
            QTextEdit {
                background-color: #1F1F1F;
                color: #FFFFFF;
                border-radius: 10px;
                border: none;
                padding: 8px;
                background-attachment: fixed;
            }
            QScrollBar:vertical {
               border: none;
               background-color: transparent;
               width: 16px;
               margin: 16px 0 16px 0;
               border-radius:8px;
            }
            QScrollBar::handle:vertical {
               background: #989898;
               min-height: 20px;
               border-radius: 8px;
               width:10px;
            }
            QScrollBar::add-line:vertical {
               background-color: transparent;
               height: 14px;
               subcontrol-position: bottom;
               subcontrol-origin: margin;
               border: 2px solid transparent;
               width: 16px;
            }
            QScrollBar::sub-line:vertical {
               background-color: transparent;
               height: 14px;
               subcontrol-position: top;
               subcontrol-origin: margin;
               border: 2px solid transparent;
               width: 16px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
               background-color: none;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: 2px solid grey;
                width: 2px;
                height: 2px;
                background: white;
            }
        """)

        text_area_width = int(self.width() * 0.95) # max width limit
        # create widgets
        big_label = QLabel("YT downloader", self)
        big_label.setAlignment(Qt.AlignCenter) # Center alignment
        big_label.setStyleSheet("margin-bottom: 16px") # add/overwrite styles

        small_label = QLabel("Paste your link here:", self)
        small_label.setAlignment(Qt.AlignCenter) # Center alignment
        small_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        small_label.setMaximumWidth(text_area_width)

        self.input_field = QLineEdit(self)
        self.input_field.setMaximumWidth(text_area_width)

        self.button = QPushButton("Download", self)
        self.button.setMaximumWidth(text_area_width)
        # all the button related things under here are to ensure it activates when the Enter key is pressed
        self.button.clicked.connect(self.button_click)
        self.button.setAutoDefault(True)
        self.button.setDefault(True)
        self.button.setFocusPolicy(Qt.StrongFocus)
        self.button.setFocus()
        shortcut = QShortcut(Qt.Key_Return, self)
        shortcut.activated.connect(self.button.click)

        text_area = QTextEdit(self)
        text_area.setReadOnly(True)
        scroll_bar = text_area.verticalScrollBar() # needed to style the scroll bar (as limited as it is the default one is just ugly)
        text_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        small_label2 = QLabel("Console", self)
        small_label2.setAlignment(Qt.AlignCenter) # Center alignment
        small_label2.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")

        # set text area width
        text_area.setMaximumWidth(text_area_width)

        # create layouts
        v_layout = QVBoxLayout()
        sub_layout5 = QHBoxLayout()
        sub_layout5.addWidget(big_label)
        sub_layout5.setContentsMargins(10, 5, 10, 0)
        sub_layout5.setSpacing(10)
        v_layout.addLayout(sub_layout5)

        # create a sub-layout for the small label and input field
        sub_layout = QHBoxLayout()
        sub_layout.addWidget(small_label)
        sub_layout.addWidget(self.input_field)
        sub_layout.setContentsMargins(10, 0, 10, 10)
        sub_layout.setSpacing(10)
        v_layout.addLayout(sub_layout)
        
        sub_layout3 = QHBoxLayout()
        sub_layout3.addWidget(self.button)
        sub_layout3.setContentsMargins(10, 5, 10, 0)
        sub_layout3.setSpacing(10)
        v_layout.addLayout(sub_layout3)

        sub_layout4 = QHBoxLayout()
        sub_layout4.addWidget(small_label2)
        sub_layout4.setContentsMargins(10, 10, 0, 10)
        sub_layout4.setSpacing(10)
        v_layout.addLayout(sub_layout4)

        sub_layout2 = QHBoxLayout()
        sub_layout2.addWidget(text_area)
        sub_layout2.setContentsMargins(10, 0, 10, 10)
        sub_layout2.setSpacing(10)
        v_layout.addLayout(sub_layout2)

        h_layout = QHBoxLayout()
        h_layout.addLayout(v_layout) # add vertical layouts to a horizontal one

        # set main layout
        self.setLayout(h_layout)

        # redirect stdout to text area
        sys.stdout = PrintLogger(text_area)

        # set options for logger
        optionsUrl = {
            "logger": LoggerOutputs()
        }

    def button_click(self):
        link = self.input_field.text()
        self.DownloaderStart(link)
        
    x = threading.Thread(target=PrintLogger, args=(1,))  # that's needed for the console to print stuff in real time instead of at the end of the script
    x.start()
    def Downloader(self, link):    # lots of commenting here, oh boy
        optionsUrl = {
            "logger": LoggerOutputs()  #inputing them again since I can't be bothered grabbing them from a method above
        }
        url = str(link)
        print('Dowloading: '+url+'\n')   
        try:
            video_info = yt_dlp.YoutubeDL(optionsUrl).extract_info(url = url,download=False)  # this line extracts info about the vid you're trying to pira...er... download like name and similar stuff
        except DownloadError:
            print("Something went wrong!\n\nCheck the link\n\n")
            # if the url is somehow wrong (or non existant) it give you an error instead of just nothing and some technical info in the console (which doesn't show up after compiling with pyinstaller)
        year = video_info['upload_date']    # this is for metatags later
        filename = fr"{video_info['title']}"   # filename based on the video title
        newFilename = list(filename)   # I'm sanitizing the title here, because yt_dlp sanitizes it down the lane, but mutagen doesn't 
        for i in range (0, len(newFilename)):   # yt_dlp doesn't spit out the sanitized name either so it creates errors with "missing file" when certain characters are in the video title
            if newFilename[i] == '|' and newFilename[i] == '"' and newFilename[i] == '?':
                newFilename[i] = '#'
        filename = ''.join(newFilename)         
        filePath = musicDir+"/Downloaded/" + filename  # here I set the path to the save file TODO: create an option to select it manually at some point (unless I decide that I'd rather port it to Android, we'll see)
        options={'format':'bestaudio/best', 'keepvideo':False, 'outtmpl':filePath, 'addmetadata':True,  # options for downloader: bestaudio, no video and metadata support (which borks the file anyway on its own if you try to actually edit the metadata)
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegMetadata', 
            }
            ]}
        
        yt_dlp.YoutubeDL(options).download([video_info['webpage_url']])  # and here's the downloader itself

        metatag = EasyID3(filePath+'.mp3')  # every single line starting with metatag uses mutagen to add metatags. Sample metatags of course, just so it looks good, I always use AutomaTag on Android to actually tag my songs anyway TODO: Allow the users to input metatags themselves before this step 
        metatag['title'] = video_info['title']  # it's really only needed because of yt_dlp borking files when you try to edit metatags later with something like AutomaTag. Might be due to my incorrect installation of FFmpeg tho, idk
        metatag['artist'] = "Unknown"
        metatag['date'] = year[0:4]
        metatag.RegisterTextKey("track", "TRCK")
        metatag['track'] = ''
        metatag.save()      
        print('\n Finished!\n')  # these 1 line informs the user that it's done
            

    def DownloaderStart(self, link, event=None): # thats needed to run the downloader and the console at the same time. If they were on the same thread the console would just spit out everything at once at the end
        y = threading.Thread(target=self.Downloader, args=(link,))
        y.start()
    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

