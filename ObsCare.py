from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from ui.play_ui import *
from Detect.DetectVideo import Model, ImageViewer

import cv2

# Display : 사용할 thread, Model 객체를 한번에 관리하기 위한 클래스 
class Display:
    # __int__ : 생성자
    # camnum : Model 생성할 카메라 번호
    # alert: 로그 알람을 위해 받은 ui 파일의 list
    # image_viewer : 영상 재생에 대한 객체
    def __init__(self, camnum, alert, image_viewer):
        self.image_viewer = image_viewer
        self.thread = QtCore.QThread()
        self.vid = Model(None, camnum, alert)
    
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

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # ui.play_ui의 WindowClass 이용하여 창 객체 생성
    myWindow = WindowClass()
    
    # 영상 재생에 대한 객체 생성
    image_viewer = []
    image_viewer.append(ImageViewer())
    image_viewer.append(ImageViewer())
    image_viewer.append(ImageViewer())
    image_viewer.append(ImageViewer())
    
    # 현재 접근 가능한 카메라 확인 및 displaylist로 연결 가능한 카메라 수만큼 Display 객체 생성
    displaylist = []
    img_idx = 0
    for i in range(10):
        if cv2.VideoCapture(i).isOpened():
            displaylist.append(Display(i, myWindow.alert_browser, image_viewer[img_idx]))
            img_idx += 1
    

    # displaylist에 포함되어있는 Display 객체의 영상 재생
    for display in displaylist:
        display.startDisplay()

    # if length >= 1:
    #     thread1 = QtCore.QThread()
    #     thread1.start()
    #     vid1 = Model(None, camNums[0], myWindow.alert_browser)
    #     vid1.moveToThread(thread1)
    #     vid1.VideoSignal.connect(image_viewer1.setImage)
    #     start_button1 = QtWidgets.QPushButton()
    #     start_button1.clicked.connect(vid1.startDetecting)
    #     start_button1.click()
        

    # video_layout에 영상 행, 열로 추가
    myWindow.video_layout.addWidget(image_viewer[0], 0, 0)
    myWindow.video_layout.addWidget(image_viewer[1], 0, 1)
    myWindow.video_layout.addWidget(image_viewer[2], 1, 0)
    myWindow.video_layout.addWidget(image_viewer[3], 1, 1)

    # 전체화면으로 실행
    myWindow.showFullScreen()
    # app 실행
    app.exec_()

    # app 종료 후 생성한 Model 객체 스트리밍 정지
    for display in displaylist:
        display.stopDisplay()
    # if length >= 1:
    #     vid1.stopDetecting()
    #     thread1.quit()

    # 시스템 종료
    sys.exit()
