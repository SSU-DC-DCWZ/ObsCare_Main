from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore
from ui.play_prev import *
from DB_video.videoDB import *
import sys
import os

# resource_path() : 프로그램 빌드 시 경로 설정을 위한 함수
# relative_path : 사용중인 상대 경로
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# 프로그램 빌드 시에는 resource_path()로 반환된 경로를 사용하고
# 터미널에서 실행할 때는 상대경로를 사용하도록 설정
form = resource_path("./ui/main.ui")
if os.path.isfile(form):
    form_class = uic.loadUiType(form)[0]
else:
    form_class = uic.loadUiType("./ui/main.ui")[0]

# WindowClass : main 화면을 띄우는데 사용되는 class
# form_class : 해당 class에 적용되는 ui
class WindowClass(QMainWindow, form_class):
    # UI파일 연결
    # 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야 한다.
    # form_class = uic.loadUiType("main.ui")[0]

    # __init__() : 생성자
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.exit_button.clicked.connect(lambda : self.close()) # 나가기 버튼
        self.action_prev_video.triggered.connect(self.get_find_date)    # 이전 영상 보기 메뉴와 연결

     # get_find_date : 입력받은 카메라 번호와 날짜로 영상 재생 위함
    def get_find_date(self):
        # 찾고자하는 영상의 정보 입력
        info, ok = QInputDialog.getText(self, 'FindVideo', '카메라 번호 - 날짜를 입력하시오 (0-20210101) : ')

        if ok:
            try : 
                # 입력한 정보에서 cam 번호와 date 추출
                self.cam, self.date = info.split('-')
            except ValueError: # 양식에 맞춰 입력하지 않았을 경우
                QMessageBox.about(self, "Error!", "올바르지 않은 입력입니다.")
                return self.get_find_date()
            
            # 입력한 정보를 바탕으로 DB에서 해당 영상의 주소 받아오기 위함
            finddb = DBvideo()
            get_path = finddb.findrecord(self.cam, self.date)

            if get_path == '':  # 해당 입력에 대한 영상이 존재하지 않을 경우
                QMessageBox.about(self, "Error!", "해당 입력에 대한 파일이 존재하지 않습니다.")
                return self.get_find_date()

            self.PrevVideo = PrevVideo(get_path) # 이전 영상 재생 객체 생성
            self.PrevVideo.show()
