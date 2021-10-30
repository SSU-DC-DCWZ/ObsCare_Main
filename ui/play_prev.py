import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, QUrl, QCoreApplication
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5 import uic
from DB_video.videoDB import *
import datetime
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
form = resource_path("./ui/prev_player.ui")
if os.path.isfile(form):
    pass
else:
    form = "./ui/prev_player.ui"

# pixel density를 높이기 위한 선언
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

# PrevVideo : 이전 영상 재생 위한 class
# QWidget : pyqt의 widget 이용하여 창 생성 위함
class PrevVideo(QWidget):
    # __init__() : 생성자
    # path : 재생하고자 하는 영상의 경로
    def __init__(self, path="./test.avi"):
        super().__init__()
        # PyQt Designer를 이용하여 생성한 ui파일 불러오기
        uic.loadUi(form, self)

        # QtWidgets의 QMediaPlayer로 movie player 틀 생성
        # prev_player.ui의 view를 self.vp로 대입
        self.mp = QMediaPlayer()
        self.vp = self.view

        self.mp.setVideoOutput(self.vp) # QMediaPlayer 틀에 video player 대입
        path = os.path.abspath(path)
        self.content = QMediaContent(QUrl.fromLocalFile(path)) # 해당 주소에서 영상 불러오기
        self.mp.setMedia(self.content) # mp에 영상 대입
        self.mp.play() # 재생 상태를 기본으로 설정
        self.state.setText("재생") # 영상 상태를 label에 출력하도록

        self.play_signal = True # 재생 상태 기록 위한 변수

        # 영상 길이 계산 위함
        temp_vid = cv2.VideoCapture(path)
        temp_vid.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
        self.vid_length = temp_vid.get(cv2.CAP_PROP_POS_MSEC)
        self.vid_length = self.calc_time(self.vid_length)

        # 계산한 영상 길이로 재생 바 범위 결정
        self.bar.setRange(0, self.vid_length[0])

        # 슬라이더 위치 변동 시
        self.bar.sliderMoved.connect(self.barChanged)

        # 각 버튼별 함수 연결
        self.btn_play_pause.clicked.connect(self.clickPlayPause)
        self.btn_exit.clicked.connect(lambda:self.close())
        self.btn_change.clicked.connect(self.change_file)

        # 각 상태별 함수 연결
        self.mp.stateChanged.connect(self.mediaStateChanged)
        self.mp.durationChanged.connect(self.durationChanged)
        self.mp.positionChanged.connect(self.positionChanged)

    # change_file() : 다른 영상으로 변경하고자 하는 경우
    def change_file(self):
         # 영상 정보 입력
        info, ok = QInputDialog.getText(self, 'FindVideo', '카메라 번호 - 날짜를 입력하시오 (0-20210101) : ')

        if ok:
            try :
                # 입력 받은 info를 카메라 번호와 날짜로 분리
                self.cam, self.date = info.split('-')
            except ValueError:  # 양식에 맞춰 입력하지 않았을 경우
                QMessageBox.about(self, "Error!", "올바르지 않은 입력입니다.")
                return self.change_file()   # 재입력 요청
            
            # DBvideo 객체 생성
            finddb = DBvideo()
            get_path = finddb.findrecord(self.cam, self.date)   # 사용자가 입력한 정보에 대한 영상 주소를 db에서 추출

            if get_path == '':  # 해당 정보에 대한 영상이 존재하지 않을 경우
                QMessageBox.about(self, "Error!", "해당 입력에 대한 파일이 존재하지 않습니다.")
                return self.change_file()

            # 찾은 영상 재생
            self.hide() # 현재 열려있는 창 숨기기
            get_path = os.path.abspath(get_path)
            self.PrevVideo = PrevVideo(get_path) # 객체 생성하고 인자로 받은 path의 영상 재생하도록
            self.PrevVideo.show() # PrevVideo 창 띄우기

    # calc_time() : sec 단위의 영상 길이 계산 위함
    # sec : 영상 길이
    # int(intoS), res : 실제 영상 길이를 int type으로 바꾼 값과 시:분:초 형태로 만든 str 반환
    def calc_time(self, sec):   # sec를 시간으로 변경
        sec = sec / 60 // 0.1 * 6
        intoS = sec

        res = ""
        temp = int(sec//3600)
        res += str(temp) + ":"
        temp = int(sec/60)
        if len(str(temp)) == 1:
            res += "0"
        res += str(temp) + ":" + str(int(sec%60))

        return int(intoS), res

    # clickPlayPause() : 재생 버튼에 연결된 함수. 영상 재생과 일시정지 기능
    def clickPlayPause(self):
        # 영상이 재생중일 때 play/pause 버튼 클릭 시 일시정지
        if self.play_signal == True:
            self.mp.pause()
            self.play_signal = False
        # 영상이 일시정지 상태일 때 play/pause 버튼 클릭 시 영상 재생
        else:
            self.mp.play()
            self.play_signal = True

    # mediaStateChanged() : 재생 상태를 QLabel로써 기록 위함
    # state : 현재 영상의 재생 상태
    def mediaStateChanged(self, state):
        msg = ''
        if state == QMediaPlayer.StoppedState:
            msg = '정지'
        elif state == QMediaPlayer.PlayingState:
            msg = '재생'
        else:
            msg = '일시정지'
        self.updateState(msg)

    # durationChanged() : 영상 길이에 따른 bar 범위 조정
    # duration : 영상 길이
    def durationChanged(self, duration):
        self.bar.setRange(0, duration)

    # positionChanged() : 사용자의 영상 재생 위치 변경에 따른 함수
    # pos : 현재 재생 위치
    def positionChanged(self, pos):
        self.bar.setValue(pos)
        self.updatePos(pos)

    # barChanged() : 재생 상태 슬라이더 움직였을 경우 현재 위치 이동
    def barChanged(self, pos):
        self.mp.setPosition(pos)

    # updateState() : stateChanged Signal 발생시 재생 상태 변경하여 출력
    def updateState(self, msg):
        self.state.setText(msg)

    # updateBar() : 동영상 file 변경될 때마다 현재 동영상의 재생시간으로 슬라이더 범위 초기화
    # duration : 동영상 길이
    def updateBar(self, duration):
        self.bar.setRange(0, duration)
        self.bar.setSingleStep(int(duration / 10))
        self.bar.setPageStep(int(duration / 10))
        self.bar.setTickInterval(int(duration / 10))
        td = datetime.timedelta(milliseconds=duration)
        stime = str(td)
        idx = stime.rfind('.')
        self.duration = stime[:idx]

    # updatePos() : 현재 재생 위치 기록 및 update
    # pos : 현재 재생 위치
    def updatePos(self, pos):
        self.bar.setValue(pos)
        td = datetime.timedelta(milliseconds=pos)
        stime = str(td)
        idx = stime.rfind('.')
        stime = f'{stime[:idx]}'
        self.playtime.setText(stime)
