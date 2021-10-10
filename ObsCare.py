from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from ui.play_ui import *
from Detect.DetectVideo import Model, ImageViewer

import cv2

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # ui.play_ui의 WindowClass 이용하여 창 객체 생성
    myWindow = WindowClass()
    
    # 영상 재생에 대한 객체 생성
    image_viewer1 = ImageViewer()
    image_viewer2 = ImageViewer()
    image_viewer3 = ImageViewer()
    image_viewer4 = ImageViewer()
    
    # 현재 접근 가능한 카메라 확인 
    camNums = []
    for i in range(10):
        tmp = cv2.VideoCapture(i)
        if tmp.isOpened():
            camNums.append(i)
        tmp.release()
    
    # 접근 가능한 카메라 대수
    length = len(camNums)
    
    # 각 카메라별로
    # thread 생성
    # 카메라 번호를 이용하여 객체 생성
    # thread와 카메라 객체 연결
    # 영상 재생을 위한 배경과 카메라 신호 연결
    # 영상 재생
    if length >= 1:
        thread1 = QtCore.QThread()
        thread1.start()
        vid1 = Model(None, camNums[0], myWindow.alert_browser)
        vid1.moveToThread(thread1)
        vid1.VideoSignal.connect(image_viewer1.setImage)
        start_button = QtWidgets.QPushButton()
        start_button.clicked.connect(vid1.startDetecting)
        start_button.click()
        
    # if length >= 2:
    #     thread2= QtCore.QThread()
    #     thread2.start()
    #     vid2 = Model(None, camNums[1], myWindow.alert_browser)
    #     vid2.moveToThread(thread2)
    #     vid2.VideoSignal.connect(image_viewer2.setImage)
    #     start_button2 = QtWidgets.QPushButton()
    #     start_button2.clicked.connect(vid2.startDetecting)
    #     start_button2.click()
        
    # if length >= 3:
    #     thread3 = QtCore.QThread()
    #     thread3.start()
    #     vid3 = Model(None, camNums[2], myWindow.alert_browser)
    #     vid3.moveToThread(thread3)
    #     vid3.VideoSignal.connect(image_viewer3.setImage)
    #     start_button3 = QtWidgets.QPushButton()
    #     start_button3.clicked.connect(vid3.startDetecting)
    #     start_button3.click()
        
    # if length >= 4:
    #     thread4 = QtCore.QThread()
    #     thread4.start()
    #     vid4 = Model(None, camNums[3], myWindow.alert_browser)
    #     vid4.moveToThread(thread4)
    #     vid4.VideoSignal.connect(image_viewer4.setImage)
    #     start_button4 = QtWidgets.QPushButton()
    #     start_button4.clicked.connect(vid4.startDetecting)
    #     start_button4.click()



    # video_layout에 영상 행, 열로 추가
    myWindow.video_layout.addWidget(image_viewer1, 0, 0)
    myWindow.video_layout.addWidget(image_viewer2, 0, 1)
    myWindow.video_layout.addWidget(image_viewer3, 1, 0)
    myWindow.video_layout.addWidget(image_viewer4, 1, 1)

    # 전체화면으로 실행
    myWindow.showFullScreen()
    # app 실행
    app.exec_()
    # app 종료 후 생성한 Model 객체 스트리밍 정지
    if length >= 1:
        vid1.stopDetecting()
        thread1.quit()
    # if length >= 2:
    #     vid2.stopDetecting()
    #     thread2.quit()
    # if length >= 3:
    #     vid3.stopDetecting()
    #     thread3.quit()
    # if length >= 4:
    #     vid4.stopDetecting()
    #     thread4.quit()
        
    # 시스템 종료
    sys.exit()
