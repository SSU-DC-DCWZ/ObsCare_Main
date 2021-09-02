import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, QUrl, QCoreApplication
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5 import uic
from DB_video.videoDB import *
import datetime
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form = resource_path("./ui/prev_player.ui")
if os.path.isfile(form):
    pass
else:
    form = "./ui/prev_player.ui"

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)


class PrevVideo(QWidget):

    def __init__(self, path="./test.avi"):
        super().__init__()
        uic.loadUi(form, self)

        self.mp = QMediaPlayer()
        self.vp = self.view

        self.mp.setVideoOutput(self.vp)
        path = os.path.abspath(path)
        self.content = QMediaContent(QUrl.fromLocalFile(path))
        self.mp.setMedia(self.content)
        self.mp.play() # default state : video playing
        self.state.setText("재생")

        self.play_signal = True

        # with video length
        temp_vid = cv2.VideoCapture(path)
        temp_vid.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
        self.vid_length = temp_vid.get(cv2.CAP_PROP_POS_MSEC)
        self.vid_length, self.vid_time = self.calc_time(self.vid_length)

        self.bar.setRange(0, self.vid_length)


        self.bar.sliderMoved.connect(self.barChanged)

        # signals
        self.btn_play_pause.clicked.connect(self.clickPlayPause)
        self.btn_exit.clicked.connect(lambda:self.close())
        self.btn_change.clicked.connect(self.change_file)

        self.mp.stateChanged.connect(self.mediaStateChanged)
        self.mp.durationChanged.connect(self.durationChanged)
        self.mp.positionChanged.connect(self.positionChanged)

    def change_file(self):
        info, ok = QInputDialog.getText(self, 'FindVideo', '카메라 번호 - 날짜를 입력하시오 (0-20210101) : ')

        if ok:
            try :
                self.cam, self.date = info.split('-')
            except ValueError:
                QMessageBox.about(self, "Error!", "올바르지 않은 입력입니다.")
                return self.change_file()
            
            finddb = DBvideo()
            get_path = finddb.findrecord(self.cam, self.date)

            if get_path == '':
                QMessageBox.about(self, "Error!", "해당 입력에 대한 파일이 존재하지 않습니다.")
                return self.change_file()

            self.hide()
            get_path = os.path.abspath(get_path)
            self.PrevVideo = PrevVideo(get_path)
            self.PrevVideo.show()



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


    # 재생 버튼
    def clickPlayPause(self):
        if self.play_signal == True:
            self.mp.pause()
            self.play_signal = False
        else:
            self.mp.play()
            self.play_signal = True

    def mediaStateChanged(self, state):
        msg = ''
        if state == QMediaPlayer.StoppedState:
            msg = '정지'
        elif state == QMediaPlayer.PlayingState:
            msg = '재생'
        else:
            msg = '일시정지'
        self.updateState(msg)

    def durationChanged(self, duration):
        self.bar.setRange(0, duration)

    def positionChanged(self, pos):
        self.bar.setValue(pos)
        self.updatePos(pos)

    # 마우스로 재생 상태 슬라이더 움직이면 호출됨
    # 동영상의 재생 시간을 범위로 가짐.
    def barChanged(self, pos):
        self.mp.setPosition(pos)

    # 현재 상태(play, stop, pause) 바뀔 때마다 호출.
    # stateChanged 시그널 발생 시 widget으로 전달됨
    def updateState(self, msg):
        self.state.setText(msg)

    # 동영상 file이 변경될 때마다 호출
    # durationChanged signal 발생 시 위젯으로 재생시간(ms) 전달됨
    # 현재 동영상파일의 재생시간으로 슬라이더 범위 초기화
    def updateBar(self, duration):
        self.bar.setRange(0, duration)
        self.bar.setSingleStep(int(duration / 10))
        self.bar.setPageStep(int(duration / 10))
        self.bar.setTickInterval(int(duration / 10))
        td = datetime.timedelta(milliseconds=duration)
        stime = str(td)
        idx = stime.rfind('.')
        self.duration = stime[:idx]

    # 동영상 파일 재생될 때마다 기본 1초 간격으로 호출되는 함수
    # 현재 재생 위치 전달됨
    def updatePos(self, pos):
        self.bar.setValue(pos)
        td = datetime.timedelta(milliseconds=pos)
        stime = str(td)
        idx = stime.rfind('.')
        stime = f'{stime[:idx]} / {self.vid_time}'
        self.playtime.setText(stime)
