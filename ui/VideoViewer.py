from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
from ui.play_ui import *
from Detect.DetectVideo import Model

# Display : 사용할 thread, Model 객체를 한번에 관리하기 위한 클래스
class Display:
    # __int__ : 생성자
    # source : 영상 소스(카메라 번호 또는 영상의 경로)
    # alert: 로그 알람을 위해 받은 ui 파일의 list
    # image_viewer : 영상 재생에 대한 객체
    def __init__(self, source, display, alert, image_viewer):
        self.image_viewer = image_viewer
        self.thread = QtCore.QThread()
        self.vid = Model(None, source, display, alert)

    # startDisplay : 각 카메라별로 thread, Model 객체 생성 및 thread와 Model 객체 연결, 영상 재생을 위한 배경과 카메라 신호 연결, 영상 재생
    def startDisplay(self):
        self.thread.start()
        self.vid.moveToThread(self.thread)
        self.vid.VideoSignal.connect(self.image_viewer.setImage)
        self.start_button = QtWidgets.QPushButton()
        self.start_button.clicked.connect(self.vid.startDetecting)
        self.start_button.click()

    # stopDisplay : app 종료 후 생성한 Model 객체 스트리밍 정지
    def stopDisplay(self):
        self.vid.stopDetecting()
        self.thread.quit()

# ImageViewer : 영상 재생하기 위한 board class
# QtWidgets.QWidget : qt에서의 board 생성 위해 상속
class ImageViewer(QtWidgets.QWidget):
    # __init__ : 생성자
    # parent : 상속한 class
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.image = QtGui.QImage()
        # paint event 받았을 때 해당 widget에서 모든 pixel을 직접 그림으로써 적은 최적화 제공
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        self.setFixedSize(853, 480)

    # paintEvent : board에 image 삽입 위한 함수
    # event : WA_OpaquePaintEvent 위한 event
    def paintEvent(self, event):
        # QtGui.QPainter 이용하여 board에 image의 pixel별로 기록
        painter = QtGui.QPainter(self)
        # painter에 self.image를 input으로 주어줌. self.rect() 이용하여 비율에 따라 그려지도록 함
        painter.drawImage(self.rect(), self.image)
        self.image = QtGui.QImage()

    # videosignal 받을 시 아래 함수 수행
    # setImage : 카메라로 촬영하는 image에 대한 초기화
    # image : camera로 받아오는 image
    @pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        # image가 없을 경우. (오류 처리)
        if image.isNull():
            print("Viewer Dropped frame!")

        self.image = image
        # image 크기와 판 크기가 상이할 경우 판 크기로 맞춤
        if image.size() != self.size():
            self.setFixedSize(QtCore.QSize(853, 480))
        self.update()