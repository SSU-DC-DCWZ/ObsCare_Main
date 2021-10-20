from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5 import QtCore
from ui.play_prev import *
from DB_video.videoDB import *
import sys
import os
import time

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

    # __init__ : 생성자
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowIcon(QIcon('./img/web.png'))  # 창 아이콘 생성

        self.setUI()  # UI 파일 가져오기

        self.real_labels = [self.box1, self.box2, self.box3, self.box4]  # 테두리 창들로 이뤄진 list
        self.btn_info = {}  # btn : 몇 번 화면 으로 구성된 dict
        self.alert_cnt = [0 for _ in range(4)]  # 현재 특정 위치에 알림이 몇 개 생겼는지 확인하기 위한 list

        self.action_prev_video.triggered.connect(self.get_find_date)  # 이전 영상 보기 메뉴와 연결
        self.action_help.triggered.connect(self.help_window)  # 도움말 보기 창 열기
        # self.show_alert()

    def setUI(self):
        # introduction
        window_name = QLabel("Alert List")
        window_name.setStyleSheet("color:white;")
        window_name.setFont(QFont("Roboto", 17))
        window_name.setAlignment(Qt.AlignCenter)
        self.alert_layout.addWidget(window_name)

        # 알림창에 들어갈 스크롤바 정의
        self.scroll = QScrollArea()
        tmp_widget = QWidget()

        # 알림창 생성 및 스크롤바 연결
        self.alert_list = QVBoxLayout(tmp_widget)
        self.alert_layout.addWidget(self.scroll)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(tmp_widget)
        self.scroll.setFixedWidth(400)

        # exit button
        self.exit_button = QPushButton("나가기")
        self.exit_button.clicked.connect(lambda: self.close())  # 나가기 버튼
        self.alert_layout.addWidget(self.exit_button)

    # get_find_date : 입력받은 카메라 번호와 날짜로 영상 재생 위함
    def get_find_date(self):
        # 찾고자하는 영상의 정보 입력
        info, ok = QInputDialog.getText(self, 'FindVideo', '카메라 번호 - 날짜를 입력하시오 (1-20210101) : ')
        if ok:
            try:
                # 입력한 정보에서 cam 번호와 date 추출
                self.cam, self.date = info.split('-')
            except ValueError:  # 양식에 맞춰 입력하지 않았을 경우
                QMessageBox.about(self, "Error!", "올바르지 않은 입력입니다.")
                return self.get_find_date()

            # 입력한 정보를 바탕으로 DB에서 해당 영상의 주소 받아오기 위함
            finddb = DBvideo()
            get_path = finddb.findrecord(self.cam, self.date)

            if get_path == '':  # 해당 입력에 대한 영상이 존재하지 않을 경우
                QMessageBox.about(self, "Error!", "해당 입력에 대한 파일이 존재하지 않습니다.")
                return self.get_find_date()

            self.PrevVideo = PrevVideo(get_path)  # 이전 영상 재생 객체 생성
            self.PrevVideo.show()

    # make_alert(i) : i 상황을 기준으로 alert_layout에 알림 생성
    @QtCore.pyqtSlot(datetime.datetime, int, str)
    def make_alert(self, time, location, situation):
        txt = f"**상황발생**\n시간 : {time.strftime('%H:%M:%S')}\n위치 : {str(location)}\n상황 : {situation}"  # 위치 자리에 self.num, 상황 자리에 situation
        btn = QPushButton(txt)  # 알림 관련 버튼 생성
        self.btn_info[btn] = location  # self.btn_info에 btn : 위치 정보 삽입
        btn.clicked.connect(self.end_situation)  # 버튼 클릭 시 end_situation() 함수 실행
        btn.setStyleSheet("background-color : white;")  # 버튼 스타일 지정

        self.alert_cnt[location] += 1  # 해당 위치의 알림 개수 +1
        self.real_labels[location].setStyleSheet('background-color : transparent;border:5px solid red;')  # 상황 발생 시 빨간색 테두리 생성

        self.alert_list.addWidget(btn)  # 버튼 삽입
        self.alert_list.setAlignment(Qt.AlignTop)


    # end_situation : 버튼 클릭 시 실행되는 함수로, 상황 종료를 나타내도록 함
    def end_situation(self):
        btn = self.sender()  # 클릭된 버튼 정보 받아오기
        label = self.btn_info[btn]  # 버튼이 가리키고 있는 위치 정보 받아오기

        if self.alert_cnt[label] == 1:  # 해당 위치의 알림이 모두 제거되었을 경우
            self.real_labels[label].setStyleSheet('background-color : transparent; border : none;')  # 테두리 제거
        self.alert_cnt[label] -= 1  # 해당 알림이 종료되었음을 기록

        btn.deleteLater()  # 버튼 클릭 시 상황 종료와 함께 버튼 제거
        self.btn_info.pop(btn)  # 저장되어있던 버튼 정보 제거

    # help_window : 도움말 창
    def help_window(self):
        self.help = QMessageBox()
        self.help.setStyleSheet("QLabel{min-width:400px; min-height:70px;}")
        self.help.setWindowTitle('Help')
        self.help.setIcon(QMessageBox.NoIcon)
        self.help.setText("<h2>도움말</h2>")

        infotxt = "<p>공공장소에서 눈만 돌리면 CCTV가 보인다는 말이 과언이 아닐 정도로 CCTV가 우리 생활에 깊숙이 자리 잡았습니다.</p>\
                  <p>CCTV의 대수가 급격히 늘어나면서 관리와 효율성 문제와 더불어, 곳곳에 설치된 CCTV를 개별 관제하는 것으로는\
                  응급 상황 대처 등에 실효성이 떨어질 수 있다는 지적이 대두되고 있습니다.</p>\
                  <p>이런 문제점을 해결할 수 있는 방안으로 영상을 자동으로 분석하여 문제 상황을 즉시 알리는\
                  지능형 영상 관제 시스템(ObsCare)을 제시하고자 합니다.</p>\n\n"

        self.help.setInformativeText(infotxt)
        self.help.exec_()
