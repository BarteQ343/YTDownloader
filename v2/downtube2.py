from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QScrollBar, QFileDialog, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QTextCursor, QIcon
import yt_dlp                               # for Downloading from YouTube
import os                                   # for getting os type (Win or Linux)
from mutagen.easyid3 import EasyID3         # for adding sample metadata
import sys                                  # for saving file
import datetime
from win32com.shell import shell, shellcon  # for finding out where the music library is #type: ignore
from yt_dlp.utils import DownloadError      # for error handling (duh)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))   # getting workfolder path for locating assets

global musicDir

if os.name == 'nt':                                                                 # checking if its Windows or Linux (or Mac but can't test it)
    musicDir = shell.SHGetKnownFolderPath(shellcon.FOLDERID_Music, 0, 0) 
    musicDir = musicDir+"\\Downloaded"   
elif os.name == 'posix':                                                            # also I'm doing nothing with linux yet cuz idk how to install proper version of Python on it (or rather how to tell the interpreter which one to use)
    musicDir = os.path.expanduser('~/Music')
    musicDir = musicDir+"/Downloaded"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        icon = resource_path("assets/logo.png")
        # set window properties
        self.setWindowTitle("YT downloader")
        self.setGeometry(100, 100, 570, 600)
        self.setWindowIcon(QIcon(icon))
        widget = QWidget()
        self.setCentralWidget(widget)
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

        self.input_field = QLineEdit(widget)
        self.input_field.setMaximumWidth(text_area_width)

        self.button = QPushButton("Download", widget)
        self.button.setMaximumWidth(text_area_width)
        self.button.clicked.connect(self.button_click)
        self.button.setAutoDefault(True)
        self.button.setDefault(True)
        self.button.setFocusPolicy(Qt.StrongFocus)
        self.button.setFocus()

        self.button2 = QPushButton("Select Directory", widget)
        self.button2.setMaximumWidth(text_area_width)
        self.button2.clicked.connect(self.openFileNameDialog)


        #text_area = QTextEdit(self)
        #text_area.setReadOnly(True)
        #text_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.small_label2 = QLabel("Console", widget)
        self.small_label2.setAlignment(Qt.AlignCenter) # Center alignment
        self.small_label2.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")

        self.small_label3 = QLabel(" ", widget)
        self.small_label3.setAlignment(Qt.AlignCenter) # Center alignment
        self.small_label3.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")

        self.squish = QLabel(" ", widget)
        self.squish.setAlignment(Qt.AlignCenter) # Center alignment
        self.squish.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px; margin-top:20px")

        # set text area width
        #text_area.setMaximumWidth(text_area_width)

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
        sub_layout4.addWidget(self.small_label2)
        sub_layout4.setContentsMargins(0, 0, 0, 0)
        sub_layout4.setSpacing(10)
        v_layout.addLayout(sub_layout4)

        sub_layout2 = QHBoxLayout()
        sub_layout2.addWidget(self.small_label3)
        sub_layout2.setContentsMargins(0, 0, 0, 0)
        sub_layout2.setSpacing(10)
        v_layout.addLayout(sub_layout2)

        sub_layout6 = QHBoxLayout()
        sub_layout6.addWidget(self.squish)
        sub_layout6.setContentsMargins(0, 0, 0, 0)
        sub_layout6.setSpacing(10)
        v_layout.addLayout(sub_layout6)

        h_layout = QHBoxLayout()
        h_layout.addLayout(v_layout)

        # set main layout
        widget.setLayout(h_layout)

        musicDirLoc = "Current download location:\n"+musicDir
        self.small_label2.setText(musicDirLoc)

    def button_click(self):
        link = self.input_field.text()
        self.Downloader(link)

    def openFileNameDialog(self):                               # this is used to show dir select dialog
        global musicDir
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        musicDirTmp = QFileDialog.getExistingDirectory(self,"Choose Save Directory", "", options=options)
        if musicDirTmp == "":                                           # in case the user clicks cancel it just confirms the last directory that was selected, be it the default one or a custom one
            musicDirLoc = "Current download location:\n"+musicDir
            self.small_label2.setText(musicDirLoc)
        else:
            musicDir = musicDirTmp
            musicDirLoc = "Current download location:\n"+musicDir
            self.small_label2.setText(musicDirLoc)


    def Downloader(self, link):                                                                                                   # lots of commenting here, oh boy
        url = str(link)
        print('Dowloading: '+url+'\n')
        try:
            video_info = yt_dlp.YoutubeDL().extract_info(url = url,download=False)                            # this line extracts info about the vid you're trying to pira...er... download like name and similar stuff
        except DownloadError:
            self.small_label3.setText("Something went wrong\nCheck the link")
            # if the url is somehow wrong (or non existant) it give you an error instead of just nothing
        try:
            year = video_info['upload_date']                                                                                # this is for metatags later
            year = year[0:4]
            filename = fr"{video_info['title']}"                                                                        # filename based on the video title
            self.small_label3.setText("Downloading:\n"+filename)
            QApplication.processEvents()
            newFilename = list(filename)                                                                                # I'm sanitizing the title here, because yt_dlp sanitizes it down the lane, but mutagen doesn't 
            for i in range (0, len(newFilename)):                                                                           # yt_dlp doesn't spit out the sanitized name either so it creates errors with "missing file" when certain characters are in the video title
                if newFilename[i] == '|' or newFilename[i] == '"' or newFilename[i] == '?':
                    newFilename[i] = '#'
            filename = ''.join(newFilename)      
            filePath = musicDir+"/" + filename
            filePath = str(filePath)                                                                   # here I set the path to the save file
            options={'format':'bestaudio/best', 'keepvideo':False, 'outtmpl':filePath, 'addmetadata':True,                  # options for downloader: bestaudio, no video and metadata support (which borks the file anyway on its own if you try to actually edit the metadata)
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                ]}

            yt_dlp.YoutubeDL(options).download([video_info['webpage_url']])                                                 # and here's the downloader itself
            
            title = video_info['title']
            artist = 'Unknown'
            date = year
            album = ''
            trackNr = ''

            self.show_new_window(video_info['title'], artist=video_info['channel'], date=year, filePath=filePath)
            self.small_label3.setText("Downloaded; adding metatags")
            QApplication.processEvents()

            
        except UnboundLocalError:
            self.small_label3.setText("Something went wrong\nCheck the link")

    def show_new_window(self, title, date, filePath, artist="Unknown"):
        defaultTitle = title
        defaultArtist = artist
        defaultDate = date
        filePath = filePath
        newWindow = QMainWindow(self)
        newWindow.setAttribute(Qt.WA_DeleteOnClose)
        icon = resource_path("assets/logo.png")
        # set window properties
        newWindow.setWindowTitle("YT downloader - Edit metatags")
        newWindow.setGeometry(100, 100, 570, 600)
        newWindow.setWindowIcon(QIcon(icon))
        widgetWindow2 = QWidget()
        newWindow.setCentralWidget(widgetWindow2)
        widgetWindow2.setStyleSheet("""
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
        """)

        max_width = int(newWindow.width() * 0.95)
        # Create a big, centered label
        widgetWindow2.big_label = QLabel("Edit metatags")
        widgetWindow2.big_label.setAlignment(Qt.AlignCenter)

        # Create pairs of small label and text input field
        widgetWindow2.label1 = QLabel("Title:")
        widgetWindow2.label1.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        widgetWindow2.text_input1 = QLineEdit()
        widgetWindow2.text_input1.setText(title)
        widgetWindow2.label2 = QLabel("Artist:")
        widgetWindow2.label2.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        widgetWindow2.text_input2 = QLineEdit()
        widgetWindow2.text_input2.setText(artist)
        widgetWindow2.label3 = QLabel("Year:")
        widgetWindow2.label3.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        widgetWindow2.text_input3 = QLineEdit()
        widgetWindow2.text_input3.setInputMask("9999;_")
        today = datetime.date.today()
        todayy = today.year
        if int(widgetWindow2.text_input3.text()) > todayy:
            widgetWindow2.text_input3.setText(todayy)
        widgetWindow2.text_input3.setText(date)
        widgetWindow2.label4 = QLabel("Album:")
        widgetWindow2.label4.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        widgetWindow2.text_input4 = QLineEdit()
        widgetWindow2.label5 = QLabel("Track nr:")
        widgetWindow2.label5.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 16px")
        widgetWindow2.text_input5 = QLineEdit()

        def accept_tags():
            title = widgetWindow2.text_input1.text()
            artist = widgetWindow2.text_input2.text()
            date = widgetWindow2.text_input3.text()
            album = widgetWindow2.text_input4.text()
            trackNr = widgetWindow2.text_input5.text()
            self.add_tags(title, artist, date, album, trackNr, filePath)
            self.small_label3.setText("Finished")
            newWindow.close()

        def reset():
            widgetWindow2.text_input1.setText(defaultTitle)
            widgetWindow2.text_input2.setText(defaultArtist)
            widgetWindow2.text_input3.setText(defaultDate)

        # Create two buttons
        widgetWindow2.button1 = QPushButton("Reset")
        widgetWindow2.button1.setMaximumWidth(max_width)
        widgetWindow2.button1.clicked.connect(reset)
        widgetWindow2.button2 = QPushButton("Done")
        widgetWindow2.button2.setMaximumWidth(max_width)
        widgetWindow2.button2.clicked.connect(accept_tags)

        # Create layout for small label and text input field pairs
        widgetWindow2.layout = QVBoxLayout()
        widgetWindow2.layout.addWidget(widgetWindow2.label1)
        widgetWindow2.layout.addWidget(widgetWindow2.text_input1)
        widgetWindow2.layout.addWidget(widgetWindow2.label2)
        widgetWindow2.layout.addWidget(widgetWindow2.text_input2)
        widgetWindow2.layout.addWidget(widgetWindow2.label3)
        widgetWindow2.layout.addWidget(widgetWindow2.text_input3)
        widgetWindow2.layout.addWidget(widgetWindow2.label4)
        widgetWindow2.layout.addWidget(widgetWindow2.text_input4)
        widgetWindow2.layout.addWidget(widgetWindow2.label5)
        widgetWindow2.layout.addWidget(widgetWindow2.text_input5)
        widgetWindow2.layout.setSpacing(10)

        # Create layout for buttons
        widgetWindow2.button_layout = QHBoxLayout()
        widgetWindow2.button_layout.addWidget(widgetWindow2.button1)
        widgetWindow2.button_layout.addWidget(widgetWindow2.button2)
        widgetWindow2.button_layout.setContentsMargins(10, 15, 10, 10)
        widgetWindow2.button_layout.setSpacing(10)

        # Create main layout for the new window
        widgetWindow2.main_layout = QVBoxLayout()
        widgetWindow2.main_layout.addWidget(widgetWindow2.big_label)
        widgetWindow2.main_layout.addLayout(widgetWindow2.layout)
        widgetWindow2.main_layout.addLayout(widgetWindow2.button_layout)

        # Set the main layout for the window
        widgetWindow2.setLayout(widgetWindow2.main_layout)
        newWindow.show()
        
    def add_tags(self, title, artist, date, album, trackNr, filePath):
        metatag = EasyID3(filePath+'.mp3')                         # every single line starting with metatag uses mutagen to add metatags. Sample metatags of course, just so it looks good, I always use AutomaTag on Android to actually tag my songs anyway
        metatag['title'] = title              # it's really only needed because of yt_dlp borking files when you try to edit metatags later with something like AutomaTag. Might be due to my incorrect installation of FFmpeg tho, idk
        metatag['artist'] = artist
        metatag['date'] = date
        metatag['album'] = album
        metatag.RegisterTextKey("track", "TRCK")
        metatag['track'] = trackNr
        metatag.save()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

#https://copyprogramming.com/howto/pyqt5-creating-new-window
