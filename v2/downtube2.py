from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QScrollBar, QFileDialog
from PyQt5.QtCore import Qt, QRunnable, QThreadPool
from PyQt5.QtGui import  QPainter, QTextCursor, QIcon
import yt_dlp               # for Downloading from YouTube
import os                   # for getting os type (Win or Linux)
from mutagen.easyid3 import EasyID3         # for adding sample metadata
import sys                  # for saving file
import threading            # for real time console in tkinter
from win32com.shell import shell, shellcon  # for finding out where the music library is #type: ignore               
from yt_dlp.utils import DownloadError      # for error handling (duh)
import platform
import time


app = QApplication(sys.argv)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))   # getting workfolder path for locating assets

global musicDir

if os.name == 'nt':                                 # checking if its Windows or Linux (or Mac but can't test it)
    musicDir = shell.SHGetKnownFolderPath(shellcon.FOLDERID_Music, 0, 0) 
    musicDir = musicDir+"\\Downloaded"   
elif os.name == 'posix':                            # also I'm doing nothing with linux yet cuz idk how to install proper version of Python on it (or rather how to tell the interpreter which one to use)
    musicDir = os.path.expanduser('~/Music')
    musicDir = musicDir+"/Downloaded"

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
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class Worker0(QRunnable):
    def run(self):
        def __init__(self, text_edit):
            self.text_edit = text_edit

        def write(self, message):
            self.text_edit.insertPlainText(message)
            self.text_edit.moveCursor(QTextCursor.End)
            self.text_edit.ensureCursorVisible()

        def flush(self):
            pass

class Worker1(QRunnable):
    def __init__(self, link):
        super(Worker1, self).__init__()
        self.link = link

    def run(self):
        optionsUrl = {
            "logger": LoggerOutputs()
        }
        url = str(self.link)
        print('Dowloading: '+url+'\n')                                          
        try:
            video_info = yt_dlp.YoutubeDL(optionsUrl).extract_info(url = url,download=False)            # this line extracts info about the vid you're trying to pira...er... download like name and similar stuff
        except DownloadError:
            return print("Something went wrong!\n\nCheck the link\n\n")
            # if the url is somehow wrong (or non existant) it give you an error instead of just nothing                                       # this is for metatags later
        filename = fr"{video_info['title']}"                                # filename based on the video title
        newFilename = list(filename)                                        # I'm sanitizing the title here, because yt_dlp sanitizes it down the lane, but mutagen doesn't 
        for i in range (0, len(newFilename)):                                   # yt_dlp doesn't spit out the sanitized name either so it creates errors with "missing file" when certain characters are in the video title
            if newFilename[i] == '|' or newFilename[i] == '"' or newFilename[i] == '?':
                newFilename[i] = '#'
        filename = ''.join(newFilename)      
        filePath = musicDir+"/" + filename                                   # here I set the path to the save file
        options={'format':'bestaudio/best', 'keepvideo':False, 'outtmpl':filePath, 'addmetadata':True,                  # options for downloader: bestaudio, no video and metadata support (which borks the file anyway on its own if you try to actually edit the metadata)
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            ]}
        
        yt_dlp.YoutubeDL(options).download([video_info['webpage_url']])                         # and here's the downloader itself

        global year
        year = video_info['upload_date']
        year = year[0:4]
        global title
        title = video_info['title']

        self.show_new_window()

        metatag = EasyID3(filePath+'.mp3')                 # every single line starting with metatag uses mutagen to add metatags. Sample metatags of course, just so it looks good, I always use AutomaTag on Android to actually tag my songs anyway
        metatag['title'] = video_info['title']              # it's really only needed because of yt_dlp borking files when you try to edit metatags later with something like AutomaTag. Might be due to my incorrect installation of FFmpeg tho, idk
        metatag['artist'] = "Unknown"
        metatag['date'] = year[0:4]
        metatag.RegisterTextKey("track", "TRCK")
        metatag['track'] = ''
        metatag.save()      
        print('\n Finished!\n')

    def show_new_window(self):
        self.w = NewWindow()
        self.w.show()
        return True
      
class Window(QMainWindow):
    def __init__(self):
        self.threadpool = QThreadPool()
        worker0 = Worker0()                                 # that's needed for the console to print stuff in real time instead of at the end of the script
        self.threadpool.start(worker0)
        QMainWindow.__init__(self)
        icon = resource_path("assets/logo.png")
        # set window properties
        self.setWindowTitle("YT downloader")
        self.setGeometry(100, 100, 570, 600)
        self.setWindowIcon(QIcon(icon))
        widget = QWidget()
        self.setCentralWidget(widget)
        widget.setStyleSheet("""
            QPushButton {
                border-style: solid;
                border-width: 2px;
                border-radius: 8px;
                border-color: #B0B0B0;
                padding: 5px;
                background-color: #2D2D30;
                color: #F0F0F0;
            }
            QPushButton:hover {
                border-color: #F0A202;
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                border-color: #F0A202;
                background-color: #F0A202;
                color: #2D2D30;
            }
            QWidget {
                background-color: #212121;
                color: #FFFFFF;
                font-family: Segoe UI, sans-serif;
                font-size: 14px;
            }
            QLabel {
                font-size: 32px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #2c2c2c;
                color: #FFFFFF;
                padding: 10px;
            }
            QTextEdit {
                background-color: #2c2c2c;
                color: #FFFFFF;
                padding: 10px;
            }
                """)
        # set design stylesheet
        
        text_area_width = int(self.width() * 0.95)
        # create widgets
        big_label = QLabel("YT Downloader", widget)
        big_label.setAlignment(Qt.AlignCenter) # Center alignment
        big_label.setStyleSheet("margin-bottom: 16px; margin-left: 0")

        small_label = QLabel("Paste your link here:", widget)
        small_label.setAlignment(Qt.AlignCenter) # Center alignment
        small_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        small_label.setMaximumWidth(text_area_width)

        widget.input_field = QLineEdit(widget)
        widget.input_field.setMaximumWidth(text_area_width)

        widget.button = QPushButton("Download", widget)
        widget.button.setMaximumWidth(text_area_width)
        widget.button.clicked.connect(lambda: self.button_click(widget))
        widget.button.setAutoDefault(True)
        widget.button.setDefault(True)
        widget.button.setFocusPolicy(Qt.StrongFocus)
        widget.button.setFocus()

        widget.button2 = QPushButton("Select Directory", widget)
        widget.button2.setMaximumWidth(text_area_width)
        widget.button2.clicked.connect(self.openFileNameDialog)

        text_area = QTextEdit(widget)
        text_area.setReadOnly(True)
        text_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        small_label2 = QLabel("Console", widget)
        small_label2.setAlignment(Qt.AlignCenter) # Center alignment
        small_label2.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")

        # set text area width
        text_area.setMaximumWidth(text_area_width)

        # create layouts
        v_layout = QVBoxLayout()
        sub_layout5 = QHBoxLayout()
        sub_layout5.addWidget(big_label)
        sub_layout5.setContentsMargins(10, 5, 10, 0)
        sub_layout5.setSpacing(0)
        v_layout.addLayout(sub_layout5)

        # create a sub-layout for the small label and input field
        sub_layout = QHBoxLayout()
        sub_layout.addWidget(small_label)
        sub_layout.addWidget(widget.input_field)
        sub_layout.setContentsMargins(10, 0, 10, 10)
        sub_layout.setSpacing(10)
        v_layout.addLayout(sub_layout)
        
        sub_layout3 = QHBoxLayout()
        sub_layout3.addWidget(widget.button2)
        sub_layout3.addWidget(widget.button)
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
        h_layout.addLayout(v_layout)

        # set main layout
        widget.setLayout(h_layout)

        # redirect stdout to text area
        sys.stdout = PrintLogger(text_area)
        print("Current download location:", musicDir)

        # set options for logger
        optionsUrl = {
            "logger": LoggerOutputs()
        }

    def button_click(self, widget):
        link = widget.input_field.text()
        self.DownloaderStart(link)

    def openFileNameDialog(self):               # this is used to show dir select dialog
        global musicDir
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        musicDirTmp = QFileDialog.getExistingDirectory(self,"Choose Save Directory", "", options=options)
        if musicDirTmp == "":                           # in case the user clicks cancel it just confirms the last directory that was selected, be it the default one or a custom one
            print("Current download location:", musicDir)
        else:
            musicDir = musicDirTmp
            print("Current download location:", musicDir)       


    def DownloaderStart(self, link, event=None):            # thats needed to run the downloader and the console at the same time. If they were on the same thread the console would just spit out everything at once at the end
        self.link = link
        worker = Worker1(self.link)
        self.threadpool.start(worker)

class NewWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        icon = resource_path("assets/logo.png")
        # set window properties
        self.setWindowTitle("YT downloader")
        self.setGeometry(100, 100, 570, 600)
        self.setWindowIcon(QIcon(icon))
        widget = QWidget()
        self.setCentralWidget(widget)
        icon = resource_path("assets/logo.png")
        # set window properties
        self.setWindowTitle("YT downloader - Edit metatags")
        self.setGeometry(100, 100, 570, 600)
        self.setWindowIcon(QIcon(icon))
        widget.setStyleSheet("""
            QPushButton {
                border-style: solid;
                border-width: 2px;
                border-color: #B0B0B0;
                border-radius: 8px;
                padding: 5px;
                background-color: #2D2D30;
                color: #F0F0F0;
            }
            QPushButton:hover {
                border-color: #F0A202;
                background-color: #4A4A4A;
           }
            QPushButton:pressed {
                border-color: #F0A202;
                background-color: #F0A202;
                color: #2D2D30;
            }
            QWidget {
                background-color: #212121;
                color: #FFFFFF;
                font-family: Segoe UI, sans-serif;
                font-size: 14px;
            }
            QLabel {
                font-size: 32px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #2c2c2c;
                color: #FFFFFF;
                padding: 10px;
            }
        """)

        max_width = int(self.width() * 0.95)
        # Create a big, centered label
        widget.big_label = QLabel("Edit metatags")
        widget.big_label.setAlignment(Qt.AlignCenter)

        # Create pairs of small label and text input field
        widget.label1 = QLabel("Title:")
        widget.label1.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        widget.text_input1 = QLineEdit()
        widget.text_input1.setText("test")
        widget.label2 = QLabel("Artist:")
        widget.label2.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        widget.text_input2 = QLineEdit()
        widget.label3 = QLabel("Year:")
        widget.label3.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        widget.text_input3 = QLineEdit()
        widget.label4 = QLabel("Album:")
        widget.label4.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        widget.text_input4 = QLineEdit()
        widget.label5 = QLabel("Track nr:")
        widget.label5.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        widget.text_input5 = QLineEdit()

        # Create two buttons
        widget.button1 = QPushButton("Reset")
        widget.button1.setMaximumWidth(max_width)
        widget.button2 = QPushButton("Done")
        widget.button2.setMaximumWidth(max_width)
        widget.button2.clicked.connect(self.close_handler)

        # Create layout for small label and text input field pairs
        widget.layout = QVBoxLayout()
        widget.layout.addWidget(widget.label1)
        widget.layout.addWidget(widget.text_input1)
        widget.layout.addWidget(widget.label2)
        widget.layout.addWidget(widget.text_input2)
        widget.layout.addWidget(widget.label3)
        widget.layout.addWidget(widget.text_input3)
        widget.layout.addWidget(widget.label4)
        widget.layout.addWidget(widget.text_input4)
        widget.layout.addWidget(widget.label5)
        widget.layout.addWidget(widget.text_input5)
        widget.layout.setSpacing(10)

        # Create layout for buttons
        widget.button_layout = QHBoxLayout()
        widget.button_layout.addWidget(widget.button1)
        widget.button_layout.addWidget(widget.button2)
        widget.button_layout.setContentsMargins(10, 15, 10, 10)
        widget.button_layout.setSpacing(10)

        # Create main layout for the new window
        widget.main_layout = QVBoxLayout()
        widget.main_layout.addWidget(widget.big_label)
        widget.main_layout.addLayout(widget.layout)
        widget.main_layout.addLayout(widget.button_layout)

        # Set the main layout for the window
        widget.setLayout(widget.main_layout)

    def close_handler(self):
        self.close()
    
def launch_window(window):
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    launch_window(Window)
