from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from ui.play_ui import *
from Detect.falldetect import model, ImageViewer

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    # 각각의 카메라당 thread 각각 배정
    thread1 = QtCore.QThread()
    thread1.start()
    vid1 = model(None, 0, myWindow.alert_browser)
    vid1.moveToThread(thread1)

    thread2 = QtCore.QThread()
    thread2.start()
    vid2 = model(None, 2, myWindow.alert_browser)
    vid2.moveToThread(thread2)

    thread3 = QtCore.QThread()
    thread3.start()
    vid3 = model(None, 4, myWindow.alert_browser)
    vid3.moveToThread(thread3)

    thread4 = QtCore.QThread()
    thread4.start()
    vid4 = model(None, 6, myWindow.alert_browser)
    vid4.moveToThread(thread4)

    # 영상 재생에 대한 판 객체 생성
    image_viewer1 = ImageViewer()
    image_viewer2 = ImageViewer()
    image_viewer3 = ImageViewer()
    image_viewer4 = ImageViewer()

    vid1.VideoSignal.connect(image_viewer1.setImage)
    vid2.VideoSignal.connect(image_viewer2.setImage)
    vid3.VideoSignal.connect(image_viewer3.setImage)
    vid4.VideoSignal.connect(image_viewer4.setImage)

    # 영상 재생
    start_button = QtWidgets.QPushButton()
    start_button.clicked.connect(vid1.start)
    start_button.click()
    start_button1 = QtWidgets.QPushButton()
    start_button1.clicked.connect(vid2.start)
    start_button1.click()
    start_button2 = QtWidgets.QPushButton()
    start_button2.clicked.connect(vid3.start)
    start_button2.click()
    start_button3 = QtWidgets.QPushButton()
    start_button3.clicked.connect(vid4.start)
    start_button3.click()

    # 영상 layout인 video_layout에 영상 추가
    myWindow.video_layout.addWidget(image_viewer1, 0, 0)
    myWindow.video_layout.addWidget(image_viewer2, 1, 1)
    myWindow.video_layout.addWidget(image_viewer3, 0, 1)
    myWindow.video_layout.addWidget(image_viewer4, 1, 0)

    # 전체화면으로 실행
    myWindow.showFullScreen()
    # app 실행
    app.exec_()
    # app 종료 후 생성한 model 객체 스트리밍 정지
    vid1.stop()
    vid2.stop()
    vid3.stop()
    vid4.stop()
    # 시스템 종료
    sys.exit()