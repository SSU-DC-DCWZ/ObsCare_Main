from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from ui.play_ui import *
from ui.open_video import *
from Detect.falldetect import model

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    screen_size = app.desktop().screenGeometry()
    width, height = screen_size.width(), screen_size.height()
    myWindow.setFixedSize(width, height-50)

    # 두 개 대상으로 영상 틀기 위해,,, threading 수행하고자 했음
    # thread1 = QtCore.QThread()
    # thread1.start()
    # vid1 = model(None, 0, myWindow.alert_browser)
    # vid1.moveToThread(thread1)

    thread1 = QtCore.QThread()
    thread1.start()
    vid1 = model(None, 0)
    vid1.moveToThread(thread1)

    # thread2 = QtCore.QThread()
    # thread2.start()
    # vid2 = ShowVideo(1)
    # vid2.moveToThread(thread2)

    # 영상 재생에 대한 판 객체 생성
    image_viewer1 = ImageViewer()
    image_viewer2 = ImageViewer()
    image_viewer3 = ImageViewer()
    image_viewer4 = ImageViewer()

    vid1.VideoSignal.connect(image_viewer1.setImage)
    # vid2.VideoSignal.connect(image_viewer2.setImage)

    # 영상 시작 (버튼 돌아가는 걸로 구현되어 있는데,,, 버튼 없애고 어케하는지 모르겠음)
    start_button = QtWidgets.QPushButton()
    start_button.clicked.connect(vid1.start)
    # start_button2 = QtWidgets.QPushButton()
    # start_button2.clicked.connect(vid2.start)
    start_button.click()
    # start_button2.click()

    # 영상 layout인 video_layout에 영상 추가
    myWindow.video_layout.addWidget(image_viewer1, 0, 0)
    myWindow.video_layout.addWidget(image_viewer2, 1, 1)
    myWindow.video_layout.addWidget(image_viewer3, 0, 1)
    myWindow.video_layout.addWidget(image_viewer4, 1, 0)

    myWindow.showMaximized()
    sys.exit(app.exec_())