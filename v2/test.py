import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget

class Window1(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Window 1')

class Window2(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Window 2')

def launch_window(window):
    app = QApplication(sys.argv)
    w = window()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    t1 = threading.Thread(target=launch_window, args=(Window1,))
    t2 = threading.Thread(target=launch_window, args=(Window2,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()