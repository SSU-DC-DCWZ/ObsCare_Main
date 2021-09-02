#from _typeshed import Self
import sys
import time
import datetime
from pathlib import Path
import os
import errno

import cv2
import torch
import torch.backends.cudnn as cudnn
from DB_video import videoDB
from DB_log import logDB

FILE = Path(__file__).absolute()
sys.path.append(FILE.parents[0].as_posix())  # add yolov5/ to path

from utils.datasets import LoadStreams
from utils.general import check_img_size, check_imshow,non_max_suppression, scale_coords, xyxy2xywh,set_logging, increment_path
from utils.plots import colors, plot_one_box
from utils.torch_utils import select_device,time_sync
from models.experimental import attempt_load

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot

# resource_path : 프로그램 빌드 시 경로 설정을 위한 함수
# 파리미터(relative_path)
# relative_path : 사용중인 상대 경로
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# 프로그램 빌드 시에는 resource_path()로 반환된 경로를 사용하고
# 터미널에서 실행할 때는 상대경로를 사용하도록 설정
weights = './Detect/best.pt'
weights = resource_path(weights)
if os.path.isfile(weights):
    pass
else:
    weights="./Detect/best.pt"

# model: cctv 스트리밍과 상황 감지와 감지한 상황에 대한 처리 클래스
# 상황번호 0 -
# 상황번호 1 -
# 상황번호 2 -
# 상황번호 3 -
# 상황번호 4 -
class model(QtCore.QObject):
    # 영상 출력에 대한 사용자 정의 신호
    VideoSignal = QtCore.pyqtSignal(QtGui.QImage)
    # __int__ : 생성자
    # 파라미터(classes, camNum, alert_browser, parent)
    # classes:발생한 카메라
    # camNum: 카메라 번호, PC에 연결된 카메라의 기기 번호
    # alert_browser: 로그 알람을 위해 받은 ui 파일의 list
    # parent:
    def __init__(self, classes, camNum, alert_browser=None, parent=None):
        super(model, self).__init__(parent)
        self.alert = alert_browser
        self.weights = weights
        self.source = str(camNum) # 
        self.imgsz = 640
        self.conf_thres = 0.45
        self.iou_thres = 0.45
        self.max_det=1000  # maximum detections per image
        self.device=''  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        self.view_img=True  # show results
        self.save_txt=False # save results to *.txt
        self.save_conf=False  # save confidences in --save-txt labels
        self.save_crop=False  # save cropped prediction boxes
        self.nosave=False  # do not save images/videos
        self.classes=classes # filter by class: --class 0, or --class 0 2 3
        self.agnostic_nms=False  # class-agnostic NMS
        self.augment=False  # augmented inference
        self.visualize=False  # visualize features
        self.update=False  # update all models
        self.project='./runs/detect'  # save results to project/name
        self.name='exp'  # save results to project/name
        self.exist_ok=False  # existing project/name ok, do not increment
        self.line_thickness=3  # bounding box thickness (pixels)
        self.hide_labels=False  # hide labels
        self.hide_conf=False  # hide confidences
        self.half=False
        self.running = False
        self.loadModel()
        self.list =[]

    # loadModel() :
    @torch.no_grad()
    def loadModel(self):
        self.webcam = self.source.isnumeric() or self.source.endswith('.txt') or self.source.lower().startswith(
            ('rtsp://', 'rtmp://', 'http://', 'https://'))
        # Initialize
        set_logging()
        self.device = select_device(self.device)
        # Load model
        self.model = attempt_load(self.weights, map_location=self.device)  # load FP32 model
        self.stride = int(self.model.stride.max())  # model stride
        self.imgsz = check_img_size(self.imgsz, s=self.stride)  # check image size
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names  # get class names
        self.classify = False

    
    # start() : 스트리밍 시작 설정 함수
    def start(self):
        if self.webcam:
            cudnn.benchmark = True  # set True to speed up constant image size inference
            self.dataset = LoadStreams(self.source, img_size=self.imgsz, stride=self.stride)
        # 웹캠의 영상 정보 처리
        self.width = self.dataset.w
        self.height = self.dataset.h
        fps = self.dataset.fps[0]
        # 동영상 저장 경로 설정
        now = datetime.datetime.now()
        self.starttime = datetime.datetime.now()
        self.savename = "./data/Recording/" + self.source + "/" + now.strftime('%Y%m%d') + ".avi"
        # 파일 경로 생성, 경로가 존재 하지 않을 경우 파일 경로 생성
        try:
            if not (os.path.isdir("./data/Recording/" + self.source)):
                os.makedirs(os.path.join("./data/Recording/" + self.source))
        # 생성 실패 시 오류 코드 출력
        except OSError as e:
            if e.errno != errno.EEXIST:
                print("Dir error")
            raise
        # 동영상 저장 코덱 지정 및 저장 형식 지정
        codec = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')
        self.out = cv2.VideoWriter(self.savename, codec, fps, ((int(self.width)), (int(self.height))))
        # DB에 동영상 관련 정보 저장
        db = videoDB.DBvideo(self.source, self.starttime, self.savename)
        db.makerecord()
        del db
        # run()에서 반복문이 지속되도록 running = True 설정
        self.running = True
        self.run()

    # stop(): 스트리밍 정지 및 저장 함수
    def stop(self):
        self.running = False
        self.out.release()
        del self.dataset

    # run() : 스트리밍을 진행하는 함수
    def run(self):
        # Run inference
        if self.device.type != 'cpu':
            self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(self.device).type_as(next(self.model.parameters())))  # run once
        for path, img, im0s, vid_cap in self.dataset:
            if self.running == False:
                break
            pred = self.runInference(path, img)

            for i, det in enumerate(pred):  # detections per image
                self.detection(i, det, path, img, im0s)
                # 좌우 상하 반전
                self.im0 = cv2.flip(self.im0, 1)
                self.im0 = cv2.flip(self.im0, 0)
                # 스트리밍 화면에 시간, 카메라번호 출력
                showtime = datetime.datetime.now()
                cv2.putText(self.im0, showtime.strftime('%Y/%m/%d'), (10,710), cv2.FONT_HERSHEY_DUPLEX,0.5,(255,255,255))
                cv2.putText(self.im0, showtime.strftime('%H:%M:%S'), (1200,710), cv2.FONT_HERSHEY_DUPLEX,0.5,(255,255,255))
                cv2.putText(self.im0, 'CAM' + str(0), (1200,25), cv2.FONT_HERSHEY_DUPLEX,0.7,(255,255,255))
                # 1번상황(쓰러진 사람) 발생 시
                if self.c == 1:
                    self.falldetection()
                # 2~4번상황(휠체어, 목발, 안내견) 발생 시
                if self.c >= 2:
                    self.objectdection()

                # 프레임 존재 시 프레임 출력
                if self.view_img:
                    self.loadVideo()
            # 일단위 저장을 위해 00시 00분 00초가 되면 스트리밍을 멈추고 저장 후 재시작
            now = datetime.datetime.now()
            if now.strftime('%H%M%S') == '164810':  # 일단위 저장을 위해 00시 00분 00초가 되면 스트리밍을 멈추고 재시작
                self.stop()
                self.start()

    # falldetection() :
    def falldetection(self):
        now = datetime.datetime.now()
        self.list.append(now)
        if len(self.list) >= 2:
            time = self.list[-1] - self.list[0]
        else:
            time = datetime.timedelta(0, 0, 0, 0, 0, 0, 0)
        if int(time.total_seconds()) >= 6:
            self.list = []  # 시간 초기화
        if int(time.total_seconds()) >= 5:
            print("fall is detected")
            self.screenshot(self.c)
            self.list = []  # 시간 초기화

    # objectdection() :
    def objectdection(self):
        now = datetime.datetime.now()
        self.list.append(now)
        if len(self.list) >= 2:
            time = self.list[-1] - self.list[0]
        else:
            time = datetime.timedelta(0, 0, 0, 0, 0, 0, 0)
        if int(time.total_seconds()) >= 10:
            self.list = []  # 시간 초기화
        if int(time.total_seconds()) >= 2:
            print(f'{self.c} is detected')
            self.screenshot(self.c)
            self.list = []  # 시간 초기화

    # loadVideo() : 프레임 각각에 대한 처리를 위한 함수
    def loadVideo(self):
        # 출력 형태 결정
        hi, wi = self.im0.shape[:2]
        color_swapped_image = cv2.cvtColor(self.im0, cv2.COLOR_BGR2RGB)
        qt_image1 = QtGui.QImage(color_swapped_image.data,
                                 wi,
                                 hi,
                                 color_swapped_image.strides[0],
                                 QtGui.QImage.Format_RGB888)
        # 영상 재생에 대한 신호 전송
        self.VideoSignal.emit(qt_image1)
        # 프레임 단위 저장
        self.out.write(self.im0)

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(25, loop.quit)  # 25 ms
        loop.exec_()

    # screenshot() : 상황 발생 시 스크린샷을 위한 처리
    # 파라미터(situation)
    # situation : 발생한 상황 번호
    def screenshot(self, situation):
        # 파일 경로 생성, 경로가 존재 하지 않을 경우 파일 경로 생성
        now = datetime.datetime.now()
        path = './data/Situation/' + str(situation) + '/' + now.strftime('%Y%m%d%H%M%S_' + str(situation)) + '.jpg'
        try:
            if not (os.path.isdir("./data/Situation/" + str(situation))):
                os.makedirs(os.path.join("./data/Situation/" + str(situation)))
        # 생성 실패 시 오류 코드 출력
        except OSError as e:  # 생성 실패 시 오류 코드 출력
            if e.errno != errno.EEXIST:
                print("Dir error")
            raise
        # 스크린샷 수행 및 저장, DB에 해당 정보 추가
        cv2.imwrite(path, self.im0)
        im = logDB.DBlog(now, situation, self.source, path)
        im.makerecord()
        # 로그 알림 창에 출력할 list에 발생 상황 정보 추가
        self.alert.append(f"*상황발생*\n시간 : {now.strftime('%H:%M:%S')}\n위치 : {self.source}\n상황 : {situation}\n")
        del im

    # runInference() :
    def runInference(self, path, img):
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        # Inference
        pred = self.model(img,
                     augment=self.augment,
                     visualize=increment_path(self.save_dir / Path(path).stem, mkdir=True) if self.visualize else False)[0]
        # Apply NMS
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, self.classes, self.agnostic_nms, max_det=self.max_det)
        return pred

    # detection() :
    def detection(self, i, det, path, img, im0s):
        if self.webcam:  # batch_size >= 1
            p, self.s, self.im0, frame = path[i], f'{i}: ', im0s[i].copy(), self.dataset.count

        self.p = Path(p)  # to Path
        self.s += '%gx%g ' % img.shape[2:]  # print string
        self.c = 0
        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], self.im0.shape).round()
            # Print results
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum()  # detections per class
                self.s += f"{n} {self.names[int(c)]}{'s' * (n > 1)}, "  # add to stri   
            # Write results
            for *xyxy, conf, cls in reversed(det):
                self.c = int(cls)  # integer class
                label = None if self.hide_labels else (self.names[self.c] if self.hide_conf else f'{self.names[self.c]} {conf:.2f}')
                plot_one_box(xyxy, self.im0, label=label, color=colors(self.c, True), line_thickness=self.line_thickness)

# ImageViewer() : 영상 재생하기 위한 board 클래스
class ImageViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.image = QtGui.QImage()
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        self.setFixedSize(853, 480)

    # paintEvent() :
    # 파라미터(event)
    # event :
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        # 규격 안 맞으면 가운데에 위치시키기 위해 좌표 지정
        painter.drawImage(self.rect(), self.image)
        # painter.drawImage((self.width()-self.image.width())/2, (self.height()-self.image.height())/2, self.image)
        self.image = QtGui.QImage()

    # setImage() : 신호 받을 시 수행
    # 파라미터(image)
    # image :
    @pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")

        self.image = image
        if image.size() != self.size():
            self.setFixedSize(QtCore.QSize(853, 480))
        self.update()