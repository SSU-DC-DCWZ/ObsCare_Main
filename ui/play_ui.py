from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore
from ui.play_prev import *
from DB_video.videoDB import *
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# form = resource_path("./ui/main.ui")
form = resource_path("./ui/main.ui")
if os.path.isfile(form):
    form_class = uic.loadUiType(form)[0]
else:
    form_class = uic.loadUiType("./ui/main.ui")[0]

# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    # UI파일 연결
    # 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야 한다.
    # form_class = uic.loadUiType("main.ui")[0]

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.exit_button.clicked.connect(lambda : self.close())
        self.action_prev_video.triggered.connect(self.get_find_date)
        self.show_alert(1)

    def get_find_date(self):
        info, ok = QInputDialog.getText(self, 'FindVideo', '카메라 번호 - 날짜를 입력하시오 (0-20210101) : ')

        if ok:
            try : 
                self.cam, self.date = info.split('-')
            except ValueError:
                QMessageBox.about(self, "Error!", "올바르지 않은 입력입니다.")
                return self.get_find_date()
            
            finddb = DBvideo()
            get_path = finddb.findrecord(self.cam, self.date)

            if get_path == '':
                QMessageBox.about(self, "Error!", "해당 입력에 대한 파일이 존재하지 않습니다.")
                return self.get_find_date()

            self.PrevVideo = PrevVideo(get_path)
            self.PrevVideo.show()


    def show_alert(self, code):
        # 오른쪽에 알림창에,,, 로그 띄울 거)
        self.alert_browser.setPlainText("print the logs")

        if code == 1:
            self.alert_browser.append("넘어졌대!")
