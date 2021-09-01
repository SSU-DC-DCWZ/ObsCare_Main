from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from ui.play_ui import *
from Detect.falldetect import model, ImageViewer
def main(vid1):
    app = QtWidgets.QApplication(sys.argv)
    # WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    # 두 개 대상으로 영상 틀기 위해,,, threading 수행하고자 했음
    thread1 = QtCore.QThread()
    thread1.start()
    # vid1 = model(None, 0, myWindow.alert_browser)
    vid1.moveToThread(thread1)

    # thread2 = QtCore.QThread()
    # thread2.start()
    # vid2 = model(None, 2, myWindow.alert_browser)
    # vid2.moveToThread(thread2)
    #
    # thread3 = QtCore.QThread()
    # thread3.start()
    # vid3 = model(None, 4, myWindow.alert_browser)
    # vid3.moveToThread(thread3)
    #
    # thread4 = QtCore.QThread()
    # thread4.start()
    # vid4 = model(None, 6, myWindow.alert_browser)
    # vid4.moveToThread(thread4)

    # 영상 재생에 대한 판 객체 생성
    image_viewer1 = ImageViewer()
    image_viewer2 = ImageViewer()
    image_viewer3 = ImageViewer()
    image_viewer4 = ImageViewer()

    vid1.VideoSignal.connect(image_viewer1.setImage)
    # vid2.VideoSignal.connect(image_viewer2.setImage)
    # vid3.VideoSignal.connect(image_viewer3.setImage)
    # vid4.VideoSignal.connect(image_viewer4.setImage)

    # 영상 시작 (버튼 돌아가는 걸로 구현되어 있는데,,, 버튼 없애고 어케하는지 모르겠음)
    start_button = QtWidgets.QPushButton()
    start_button.clicked.connect(vid1.start)
    start_button.click()
    # start_button1 = QtWidgets.QPushButton()
    # start_button1.clicked.connect(vid2.start)
    # start_button1.click()
    # start_button2 = QtWidgets.QPushButton()
    # start_button2.clicked.connect(vid3.start)
    # start_button2.click()
    # start_button3 = QtWidgets.QPushButton()
    # start_button3.clicked.connect(vid4.start)
    # start_button3.click()

    # 영상 layout인 video_layout에 영상 추가
    myWindow.video_layout.addWidget(image_viewer1, 0, 0)
    myWindow.video_layout.addWidget(image_viewer2, 1, 1)
    myWindow.video_layout.addWidget(image_viewer3, 0, 1)
    myWindow.video_layout.addWidget(image_viewer4, 1, 0)

    myWindow.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    vid1 = model(None, 0)
    main(vid1)
    vid1.running = False