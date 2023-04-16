from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QScrollBar, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QTextCursor, QIcon
import yt_dlp                               # for Downloading from YouTube
import os                                   # for getting os type (Win or Linux)
from mutagen.easyid3 import EasyID3         # for adding sample metadata
import sys                                  # for saving file
import threading                            # for real time console in tkinter
from win32com.shell import shell, shellcon  # for finding out where the music library is #type: ignore               
from yt_dlp.utils import DownloadError      # for error handling (duh)
import platform

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))   # getting workfolder path for locating assets

global musicDir

if os.name == 'nt':                                                                 # checking if its Windows or Linux (or Mac but can't test it)
    musicDir = shell.SHGetKnownFolderPath(shellcon.FOLDERID_Music, 0, 0) 
    musicDir = musicDir+"\\Downloaded"   
elif os.name == 'posix':                                                            # also I'm doing nothing with linux yet cuz idk how to install proper version of Python on it (or rather how to tell the interpreter which one to use)
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

class NewWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        icon = resource_path("assets/logo.png")
        # set window properties
        self.setWindowTitle("YT downloader - Edit metatags")
        self.setGeometry(100, 100, 570, 600)
        self.setWindowIcon(QIcon(icon))
        self.setStyleSheet("""
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

    def initUI(self):

        max_width = int(self.width() * 0.95)
        # Create a big, centered label
        big_label = QLabel("Edit metatags")
        big_label.setAlignment(Qt.AlignCenter)

        # Create pairs of small label and text input field
        label1 = QLabel("Title:")
        label1.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        text_input1 = QLineEdit()
        label2 = QLabel("Artist:")
        label2.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        text_input2 = QLineEdit()
        label3 = QLabel("Year:")
        label3.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        text_input3 = QLineEdit()
        label4 = QLabel("Album:")
        label4.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        text_input4 = QLineEdit()
        label5 = QLabel("Track nr:")
        label5.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        text_input5 = QLineEdit()

        # Create two buttons
        button1 = QPushButton("Reset")
        button1.setMaximumWidth(max_width)
        button2 = QPushButton("Done")
        button2.setMaximumWidth(max_width)
        button2.clicked.connect(self.accept)

        # Create layout for small label and text input field pairs
        layout = QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(text_input1)
        layout.addWidget(label2)
        layout.addWidget(text_input2)
        layout.addWidget(label3)
        layout.addWidget(text_input3)
        layout.addWidget(label4)
        layout.addWidget(text_input4)
        layout.addWidget(label5)
        layout.addWidget(text_input5)
        layout.setSpacing(10)

        # Create layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(button1)
        button_layout.addWidget(button2)
        button_layout.setContentsMargins(10, 15, 10, 10)
        button_layout.setSpacing(10)

        # Create main layout for the new window
        main_layout = QVBoxLayout()
        main_layout.addWidget(big_label)
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)

        # Set the main layout for the window
        self.setLayout(main_layout)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.new_window = None
        icon = resource_path("assets/logo.png")
        # set window properties
        self.setWindowTitle("YT downloader")
        self.setGeometry(100, 100, 570, 600)
        self.setWindowIcon(QIcon(icon))
        if platform.system() == 'Windows':
            if platform.release() == '10':
                self.setStyleSheet("""
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
            elif platform.release() == '11':
                self.setStyleSheet("""
                    QPushButton {
                        border-style: solid;
                        border-width: 2px;
                        border-radius: 8px;
                        border-color: #4F4F4F;
                        padding: 5px;
                        background-color: #1E1E1E;
                        color: #F0F0F0;
                    }
                    QPushButton:hover {
                        border-color: #2196F3;
                        color: #2196F3;
                    }
                    QPushButton:pressed {
                        background-color: #2196F3;
                        color: #FFFFFF;
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
        big_label = QLabel("YT Downloader", self)
        big_label.setAlignment(Qt.AlignCenter) # Center alignment
        big_label.setStyleSheet("margin-bottom: 16px; margin-left: 0")

        small_label = QLabel("Paste your link here:", self)
        small_label.setAlignment(Qt.AlignCenter) # Center alignment
        small_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        small_label.setMaximumWidth(text_area_width)

        self.input_field = QLineEdit(self)
        self.input_field.setMaximumWidth(text_area_width)

        self.button = QPushButton("Download", self)
        self.button.setMaximumWidth(text_area_width)
        self.button.clicked.connect(self.button_click)
        self.button.setAutoDefault(True)
        self.button.setDefault(True)
        self.button.setFocusPolicy(Qt.StrongFocus)
        self.button.setFocus()

        self.button2 = QPushButton("Select Directory", self)
        self.button2.setMaximumWidth(text_area_width)
        self.button2.clicked.connect(self.openFileNameDialog)


        text_area = QTextEdit(self)
        text_area.setReadOnly(True)
        text_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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
        sub_layout5.setSpacing(0)
        v_layout.addLayout(sub_layout5)

        # create a sub-layout for the small label and input field
        sub_layout = QHBoxLayout()
        sub_layout.addWidget(small_label)
        sub_layout.addWidget(self.input_field)
        sub_layout.setContentsMargins(10, 0, 10, 10)
        sub_layout.setSpacing(10)
        v_layout.addLayout(sub_layout)
        
        sub_layout3 = QHBoxLayout()
        sub_layout3.addWidget(self.button2)
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
        h_layout.addLayout(v_layout)

        # set main layout
        self.setLayout(h_layout)

        # redirect stdout to text area
        sys.stdout = PrintLogger(text_area)
        print("Current download location:", musicDir)

        # set options for logger
        optionsUrl = {
            "logger": LoggerOutputs()
        }

    def button_click(self):
        link = self.input_field.text()
        self.DownloaderStart(link)

    def openFileNameDialog(self):                               # this is used to show dir select dialog
        global musicDir
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        musicDirTmp = QFileDialog.getExistingDirectory(self,"Choose Save Directory", "", options=options)
        if musicDirTmp == "":                                           # in case the user clicks cancel it just confirms the last directory that was selected, be it the default one or a custom one
            print("Current download location:", musicDir)
        else:
            musicDir = musicDirTmp
            print("Current download location:", musicDir)

    '''def open_new_window(self):
            #self.new_window = NewWindow()
            #self.new_window.show()
            if self.new_window is None:
                self.new_window = NewWindow()
            self.new_window.show()'''

            
        
    x = threading.Thread(target=PrintLogger, args=(1,))                                                                 # that's needed for the console to print stuff in real time instead of at the end of the script
    x.start()
    def Downloader(self, link):                                                                                                   # lots of commenting here, oh boy
        optionsUrl = {
            "logger": LoggerOutputs()
        }
        url = str(link)
        print('Dowloading: '+url+'\n')                                                                                  
        try:
            video_info = yt_dlp.YoutubeDL(optionsUrl).extract_info(url = url,download=False)                            # this line extracts info about the vid you're trying to pira...er... download like name and similar stuff
        except DownloadError:
            print("Something went wrong!\n\nCheck the link\n\n")
            # if the url is somehow wrong (or non existant) it give you an error instead of just nothing
        year = video_info['upload_date']                                                                                # this is for metatags later
        filename = fr"{video_info['title']}"                                                                        # filename based on the video title
        newFilename = list(filename)                                                                                # I'm sanitizing the title here, because yt_dlp sanitizes it down the lane, but mutagen doesn't 
        for i in range (0, len(newFilename)):                                                                           # yt_dlp doesn't spit out the sanitized name either so it creates errors with "missing file" when certain characters are in the video title
            if newFilename[i] == '|' or newFilename[i] == '"' or newFilename[i] == '?':
                newFilename[i] = '#'
        filename = ''.join(newFilename)      
        filePath = musicDir+"/" + filename                                                                   # here I set the path to the save file
        options={'format':'bestaudio/best', 'keepvideo':False, 'outtmpl':filePath, 'addmetadata':True,                  # options for downloader: bestaudio, no video and metadata support (which borks the file anyway on its own if you try to actually edit the metadata)
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            ]}
        
        yt_dlp.YoutubeDL(options).download([video_info['webpage_url']])                                                 # and here's the downloader itself

        dialog = NewWindow()
        dialog.exec_()
     
        metatag = EasyID3(filePath+'.mp3')                         # every single line starting with metatag uses mutagen to add metatags. Sample metatags of course, just so it looks good, I always use AutomaTag on Android to actually tag my songs anyway
        metatag['title'] = video_info['title']              # it's really only needed because of yt_dlp borking files when you try to edit metatags later with something like AutomaTag. Might be due to my incorrect installation of FFmpeg tho, idk
        metatag['artist'] = "Unknown"
        metatag['date'] = year[0:4]
        metatag.RegisterTextKey("track", "TRCK")
        metatag['track'] = ''
        metatag.save()      
        print('\n Finished!\n')                                                                                         # these 3 lines inform the user that it's done and spit out the filename (with text wrapping so it doesn't exceed the size of a window)
            

    def DownloaderStart(self, link, event=None):                    # thats needed to run the downloader and the console at the same time. If they were on the same thread the console would just spit out everything at once at the end
        y = threading.Thread(target=self.Downloader, args=(link,))
        y.start()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

