from PyQt5 import QtWidgets

from ui.play_ui import *
from ui.VideoViewer import Display, ImageViewer

import cv2
import os

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # ui.play_ui의 WindowClass 이용하여 창 객체 생성
    myWindow = WindowClass()

    # 영상 재생에 대한 객체 생성
    image_viewer = []
    for i in range(4):
        image_viewer.append(ImageViewer())

    # 현재 접근 가능한 카메라 확인 및 displaylist로 연결 가능한 카메라 수만큼 Display 객체 생성
    displaylist = []
    img_idx = 0
    for i in range(10):
        if os.path.exists("/dev/video" + str(i)):
            if cv2.VideoCapture(i).isOpened():
                displaylist.append(Display(i, img_idx, image_viewer[img_idx], myWindow))
                img_idx += 1

    # displaylist에 포함되어있는 Display 객체의 영상 재생
    for display in displaylist:
        display.startDisplay()

    # video_layout에 영상 행, 열로 추가
    myWindow.video_layout.addWidget(image_viewer[0], 0, 0)
    myWindow.video_layout.addWidget(image_viewer[1], 0, 1)
    myWindow.video_layout.addWidget(image_viewer[2], 1, 0)
    myWindow.video_layout.addWidget(image_viewer[3], 1, 1)

    myWindow.box1.raise_()
    myWindow.box2.raise_()
    myWindow.box3.raise_()
    myWindow.box4.raise_()
    
    # 전체화면으로 실행
    myWindow.showFullScreen()
    # app 실행
    app.exec_()

    # app 종료 후 생성한 Model 객체 스트리밍 정지
    for display in displaylist:
        display.stopDisplay()

    # 시스템 종료
    sys.exit()
