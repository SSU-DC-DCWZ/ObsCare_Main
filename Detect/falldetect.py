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


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

weights = './Detect/best.pt'
weights = resource_path(weights)
if os.path.isfile(weights):
    pass
else:
    weights="./Detect/best.pt"

class model(QtCore.QObject):
    VideoSignal = QtCore.pyqtSignal(QtGui.QImage)
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

    
    #요구사항2 수정
    def start(self):
        if self.webcam:
            cudnn.benchmark = True  # set True to speed up constant image size inference
            self.dataset = LoadStreams(self.source, img_size=self.imgsz, stride=self.stride)
        self.width = self.dataset.w
        self.height = self.dataset.h
        fps = self.dataset.fps[0]
        now = datetime.datetime.now()
        self.starttime = datetime.datetime.now()
        self.savename = "./data/Recording/" + self.source + "/" + now.strftime('%Y%m%d') + ".avi"
        try:  # 파일 경로 생성, 경로가 존재 하지 않을 경우 파일 경로 생성
            if not (os.path.isdir("./data/Recording/" + self.source)):
                os.makedirs(os.path.join("./data/Recording/" + self.source))
        except OSError as e:  # 생성 실패 시 오류 코드 출력
            if e.errno != errno.EEXIST:
                print("Dir error")
            raise
        codec = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')
        self.out = cv2.VideoWriter(self.savename, codec, fps, ((int(self.width)), (int(self.height))))
        db = videoDB.DBvideo(self.source, self.starttime, self.savename)
        db.makerecord()
        del db
        self.running = True
        self.run()

    def stop(self):
        self.out.release()
        del self.dataset
        print("stop")

    def run(self):
        # Run inference
        if self.device.type != 'cpu':
            self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(self.device).type_as(next(self.model.parameters())))  # run once
        for path, img, im0s, vid_cap in self.dataset:
            if self.running == False:
                self.stop()
                break
            pred = self.runInference(path, img)

            for i, det in enumerate(pred):  # detections per image
                self.detection(i, det, path, img, im0s)
                showtime = datetime.datetime.now()
                self.im0 = cv2.flip(self.im0, 1)  # 좌우반전
                self.im0 = cv2.flip(self.im0, 0)  # 상하반전
                cv2.putText(self.im0, showtime.strftime('%Y/%m/%d'), (10,710), cv2.FONT_HERSHEY_DUPLEX,0.5,(255,255,255))
                cv2.putText(self.im0, showtime.strftime('%H:%M:%S'), (1200,710), cv2.FONT_HERSHEY_DUPLEX,0.5,(255,255,255))
                cv2.putText(self.im0, 'CAM' + str(0), (1200,25), cv2.FONT_HERSHEY_DUPLEX,0.7,(255,255,255)) #스트리밍 화면에 시간, 카메라번호 출력

                if self.c == 1:
                    self.falldetection()

                if self.c >= 2:
                    self.objectdection(self.c)

                # Stream results
                if self.view_img:
                    self.loadVideo(str(self.p))

            now = datetime.datetime.now()
            if now.strftime('%H%M%S') == '164810':  # 일단위 저장을 위해 00시 00분 00초가 되면 스트리밍을 멈추고 재시작
                self.stop()
                self.start()

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

    def loadVideo(self, path):
        image = self.im0
        hi, wi = image.shape[:2]
        # 출력 형태 결정
        color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        qt_image1 = QtGui.QImage(color_swapped_image.data,
                                 wi,
                                 hi,
                                 color_swapped_image.strides[0],
                                 QtGui.QImage.Format_RGB888)
        self.VideoSignal.emit(qt_image1)  # 시그널 보내기,,,?
        self.out.write(self.im0)

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(25, loop.quit)  # 25 ms
        loop.exec_()

    def screenshot(self, situation):
        now = datetime.datetime.now()
        path = './data/Situation/' + str(situation) + '/' + now.strftime('%Y%m%d%H%M%S_' + str(situation)) + '.jpg'
        try:  # 파일 경로 생성, 경로가 존재 하지 않을 경우 파일 경로 생성
            if not (os.path.isdir("./data/Situation/" + str(situation))):
                os.makedirs(os.path.join("./data/Situation/" + str(situation)))
        except OSError as e:  # 생성 실패 시 오류 코드 출력
            if e.errno != errno.EEXIST:
                print("Dir error")
            raise
        cv2.imwrite(path, self.im0)
        im = logDB.DBlog(now, situation, self.source, path)
        im.makerecord()
        self.alert.append(f"*상황발생*\n시간 : {now.strftime('%H:%M:%S')}\n위치 : {self.source}\n상황 : {situation}\n")
        del im

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

class ImageViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.image = QtGui.QImage()
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        self.setFixedSize(853, 480)

    # 한 판에 하나 영상 띄우기 위한 그런거인듯
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        # 규격 안 맞으면 가운데에 위치시키기 위해 좌표 지정
        painter.drawImage(self.rect(), self.image)
        # painter.drawImage((self.width()-self.image.width())/2, (self.height()-self.image.height())/2, self.image)
        self.image = QtGui.QImage()

    @pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")

        self.image = image
        if image.size() != self.size():
            self.setFixedSize(QtCore.QSize(853, 480))
        self.update()