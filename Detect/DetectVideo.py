# from _typeshed import Self
import sys
import time
import datetime
from pathlib import Path
import os
import errno

import cv2
import torch
import torch.backends.cudnn as cudnn

# 본 프로젝트는 YOLOv5 및 deepSORT를 바탕으로 object detection model을 custom train 시킨 모델을 사용합니다.
# YOLOv5 와 deepSORT의 라이브러리 함수들을 import해 fall detection 및 specific obeject detection 및 alert 에 필요한 parameter를 가져올 수 있게 합니다.
FILE = Path(__file__).absolute()
sys.path.append(FILE.parents[0].as_posix())  # add yolov5/ to path
torch.cuda.empty_cache()
from models.experimental import attempt_load
from utils.datasets import LoadStreams
from utils.general import check_img_size, check_imshow, non_max_suppression, scale_coords, xyxy2xywh, set_logging, \
    increment_path
from utils.plots import colors, plot_one_box
from utils.torch_utils import select_device, time_sync
from deep_sort.deep_sort import DeepSort
from utils.parser import get_config

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui

from DB_video import videoDB
from DB_log import logDB


# resource_path : 프로그램 빌드 시 경로 설정을 위한 함수
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
    weights = "./Detect/best.pt"


# compute_color_for_id : 각 바운딩박스별 id로 색상을 생성해주는 함수
def compute_color_for_id(label):
    palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)

    color = [int((p * (label ** 2 - label + 1)) % 255) for p in palette]
    return tuple(color)


# Model: cctv 스트리밍과 학습된 모델이 웹캠의 영상을 읽어와 추론하고, 추론된 결과에 따라 바운딩 박스 생성 클래스
# QtCore.QObject : Qt에서의 signal 사용 위한 상속
# 상황번호 0 - unfall
# 상황번호 1 - fall
# 상황번호 2 - wheelchair
# 상황번호 3 - guidedog
# 상황번호 4 - crutches
class Model(QtCore.QObject):
    # 영상 출력에 대한 사용자 정의 신호
    VideoSignal = QtCore.pyqtSignal(QtGui.QImage)

    AlertSignal = QtCore.pyqtSignal(datetime.datetime, int, str)

    # __int__ : 생성자
    # classes: 검출 클래스 filter by class
    # source: 영상 소스(카메라 번호 또는 영상의 경로)
    # display : 화면에 출력할 위치
    # alert_browser: 로그 알람을 위해 받은 ui 파일의 list
    # parent : 상속한 class
    def __init__(self, classes, source, display, parent=None):
        super(Model, self).__init__(parent)
        self.initDetectParameter(classes, source, display)
        self.loadModel()  # 생성자에서 loadModel() 수행

    def initDetectParameter(self, classes, source, display):
        self.weights = weights  # 모델
        self.source = str(source)  # 영상 소스
        self.num = str(display)  # 영상 표시 위치
        self.imgsz = 640  # 추론될 이미지 사이즈
        self.conf_thres = 0.45  # 추론 임계값
        self.iou_thres = 0.45  # iou 임계값
        self.max_det = 1000  # 최대 detection 개수
        self.device = ''  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        self.classes = [1, 2, 3, 4]  # 검출 클래스 filter by class: --class 0, or --class 0 2 3
        self.agnostic_nms = True  # NMS 활성화 class-agnostic NMS
        self.augment = False  # augmented inference
        self.visualize = False  # visualize features
        self.half = True  # 부동소수점을 절반으로 줄여 연산량 감소
        self.running = False  # 영상 재생 신호 설정

        self.fallTimeList = []  # falldetion timeList
        self.id = None  # 식별 id
        self.fallId = None  # falled 식별 id
        self.objectId = None  # object 식별 id
        self.notiObj = None  # notity parameter
        self.notiFall = None

    # loadModel() : 모델과 cam 매칭 및 모델 생성시 이미지 추론 설정
    @torch.no_grad()
    def loadModel(self):
        # 초기화
        self.device = select_device(self.device)
        self.half &= self.device.type != 'cpu'  # half precision only supported on CUDA
        # 모델 로드
        self.model = attempt_load(self.weights, map_location=self.device)  # load FP32 Model
        self.stride = int(self.model.stride.max())  # Model stride
        self.imgsz = check_img_size(self.imgsz, s=self.stride)  # check image size
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names  # get class names
        self.model.half()  # 모델의 부동소수점을 절반으로 줄여 연산량 감소

        # deepSORT 초기화
        cfg = get_config()
        cfg.merge_from_file("./deep_sort/deep_sort.yaml")
        self.deepsort = DeepSort(cfg.DEEPSORT.REID_CKPT,
                                 max_dist=cfg.DEEPSORT.MAX_DIST, min_confidence=cfg.DEEPSORT.MIN_CONFIDENCE,
                                 nms_max_overlap=cfg.DEEPSORT.NMS_MAX_OVERLAP,
                                 max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE,
                                 max_age=cfg.DEEPSORT.MAX_AGE, n_init=cfg.DEEPSORT.N_INIT,
                                 nn_budget=cfg.DEEPSORT.NN_BUDGET,
                                 use_cuda=True)

    # startDetecting() : 스트리밍 시작 설정 함수
    def startDetecting(self):
        cudnn.benchmark = True  # set True to speed up constant image size inference
        self.dataset = LoadStreams(self.source, img_size=self.imgsz, stride=self.stride)
        # 동영상 저장 정보 설정
        self.setSavevideo()
        # run()에서 반복문이 지속되도록 running = True 설정
        self.running = True
        self.playStream()

    # setSavevideo() : 동영상 저장 경로 및 DB 관리
    def setSavevideo(self):
        # 웹캠의 영상 정보 처리
        width = self.dataset.w
        height = self.dataset.h
        fps = self.dataset.fps[0]
        # 동영상 저장 경로 설정
        now = datetime.datetime.now()
        self.starttime = datetime.datetime.now()
        self.savename = "./data/Recording/" + str(self.num) + "/" + now.strftime('%Y%m%d') + ".mp4"
        # 파일 경로 생성, 경로가 존재 하지 않을 경우 파일 경로 생성
        try:
            if not (os.path.isdir("./data/Recording/" + str(self.num))):
                os.makedirs(os.path.join("./data/Recording/" + str(self.num)))
        # 생성 실패 시 오류 코드 출력
        except OSError as e:
            if e.errno != errno.EEXIST:
                print("Dir error")
            raise
        # 동영상 저장 코덱 지정 및 저장 형식 지정
        codec = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(self.savename, codec, fps, ((int(width)), (int(height))))
        # DB에 동영상 관련 정보 저장
        db = videoDB.DBvideo(str(self.num), self.starttime, self.savename)
        db.makerecord()
        del db

    # stopDetecting(): 스트리밍 정지 및 저장 함수
    def stopDetecting(self):
        self.running = False
        self.out.release()
        del self.dataset

    # playStream() : 스트리밍을 진행하는 함수
    def playStream(self):
        # 추론 시행
        if self.device.type != 'cpu':
            self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(self.device).type_as(
                next(self.model.parameters())))  # run once
        for path, img, im0s, vid_cap in self.dataset:
            # stop() 진입한 이후 반복문 탈출
            if not self.running:
                break
            pred = self.runInference(path, img)

            for i, det in enumerate(pred):  # 이미지 추론
                # stop() 진입한 이후 반복문 탈출
                if not self.running:
                    break
                self.detectSituation(i, det, path, img, im0s)

                # 1번상황(쓰러진 사람) 발생 시
                if self.c == 1:
                    self.processFall()
                # 2~4번상황(휠체어, 목발, 안내견) 발생 시
                if self.c >= 2:
                    self.processObject()

                # 비디오 출력
                self.loadVideo()
            # 일단위 저장을 위해 00시 00분 00초가 되면 스트리밍을 멈추고 저장 후 재시작
            now = datetime.datetime.now()
            if now.strftime('%H%M%S') == '000000':  # 일단위 저장을 위해 00시 00분 00초가 되면 스트리밍을 멈추고 재시작
                self.stopDetecting()
                self.startDetecting()

    # processFall() : 사람의 쓰러짐 감지시 5초간 쓰러짐상태로 계속 유지된다면 로그 발생
    def processFall(self):
        if self.fallId is None:
            self.fallId = self.id
        elif self.fallId != self.id:
            self.fallId = None
            self.notiFall = None
            return
        else:
            now = datetime.datetime.now()
            self.fallTimeList.append(now)

            if len(self.fallTimeList) >= 2:
                time = self.fallTimeList[-1] - self.fallTimeList[0]
            else:
                time = datetime.timedelta(0, 0, 0, 0, 0, 0, 0)

            if int(time.total_seconds()) >= 6:
                self.fallTimeList = []
            # print(time.total_seconds())
            if int(time.total_seconds()) == 5:  ##연속적 falldetect
                if self.notiFall == None:
                    self.captureSituation(self.c)
                    self.sendLog(self.c)
                    self.fallTimeList = []  ## 시간 초기화
                    self.notiFall = 1

    # processObject() : 특정 사물 감지시 로그 발생
    def processObject(self):
        if self.objectId is None:
            self.objectId = self.id
        elif self.objectId != self.id:
            self.notiObj = None
            return
        else:
            if self.objectId == self.id and self.notiObj == None:
                print("detected")
                self.captureSituation(self.c)
                self.sendLog(self.c)
                self.notiObj = 1

    # loadVideo() : 프레임 각각에 대한 처리를 위한 함수
    def loadVideo(self):
        # 스트리밍 화면에 시간, 카메라번호 출력
        showtime = datetime.datetime.now()

        dst = cv2.resize(self.im0, dsize=(1280, 720), interpolation=cv2.INTER_AREA)
        cv2.putText(dst, showtime.strftime('%Y/%m/%d'), (10, 710), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255))
        cv2.putText(dst, showtime.strftime('%H:%M:%S'), (1180, 710), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255))
        cv2.putText(dst, 'CAM' + str(self.num), (1200, 25), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255))

        # 출력 형태 결정
        hi, wi = dst.shape[:2]
        color_swapped_image = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)
        qt_image1 = QtGui.QImage(color_swapped_image.data,
                                 wi,
                                 hi,
                                 color_swapped_image.strides[0],
                                 QtGui.QImage.Format_RGB888)
        # 영상 재생에 대한 신호 전송
        self.VideoSignal.emit(qt_image1)

        # 프레임 단위 저장
        self.out.write(dst)

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(25, loop.quit)  # 25 ms
        loop.exec_()

    # captureSituation() : 상황 발생 시 스크린샷을 위한 처리
    # situation : 발생한 상황 번호
    def captureSituation(self, situation):
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
        im = logDB.DBlog(str(self.num), now, path, situation)
        im.makerecord()
        del im

    # sendLog() : 상황 발생 시 UI에 발생 상황 정보 출력
    # situation : 발생한 상황 번호
    def sendLog(self, situation):
        # 로그 알림 창에 출력할 list에 발생 상황 정보 추가
        now = datetime.datetime.now()
        # pyqt signal을 내보냄으로써 ui/play_ui.py의 make_alert 함수 실행
        if situation == 1:
            self.AlertSignal.emit(now, int(self.num), '환자 발생')
        elif situation == 2:
            self.AlertSignal.emit(now, int(self.num), '휠체어 사용자')
        elif situation == 3:
            self.AlertSignal.emit(now, int(self.num), '목발 사용자')
        elif situation == 4:
            self.AlertSignal.emit(now, int(self.num), '맹인 안내견')

    # runInference() : 받아온 영상을 바탕으로 프레임 단위로 영상 추론 실행
    # path : 이미지 경로값
    # img : 영상의 이미지프레임
    def runInference(self, path, img):
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        # 추론
        pred = self.model(img,
                          augment=self.augment,
                          visualize=increment_path(self.save_dir / Path(path).stem,
                                                   mkdir=True) if self.visualize else False)[0]
        # NMS 실행
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, self.classes, self.agnostic_nms,
                                   max_det=self.max_det)
        return pred

    # detectSituation() : 추론된 이미지에 id, class , 좌표값에 맞게 바운딩 박스 생성
    # i,det : 추론 결과
    # path : 이미지 경로
    # img : 출력될 이미지
    # im0s : 추론된 이미지
    def detectSituation(self, i, det, path, img, im0s):

        p, self.s, self.im0, frame = path[i], f'{i}: ', im0s[i].copy(), self.dataset.count
        self.p = Path(p)  # to Path
        self.s += '%gx%g ' % img.shape[2:]  # print string
        self.c = 0
        if len(det):
            # 이미지 리스케일링
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], self.im0.shape).round()
            # 결과 도출
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum()  # detections per class
                self.s += f"{n} {self.names[int(c)]}{'s' * (n > 1)}, "  # add to string

            # 바운딩 박스 생성용 변수 생성
            xywhs = xyxy2xywh(det[:, 0:4])
            confs = det[:, 4]
            clss = det[:, 5]

            # deepSORT에 추론 반영
            outputs = self.deepsort.update(xywhs.cpu(), confs.cpu(), clss, self.im0)

            # 결과 출력
            if len(outputs) > 0:
                for j, (output, conf) in enumerate(zip(outputs, confs)):
                    bboxes = output[0:4]
                    self.id = output[4]
                    cls = output[5]
                    self.c = int(cls)  # 정수화
                    label = f'{self.id} {self.names[self.c]} {conf:.2f}'
                    color = compute_color_for_id(self.id)
                    plot_one_box(bboxes, self.im0, label=label, color=color,
                                 line_thickness=2)  # 이미지 위에 출력될 바운딩 박스를 생성합니다.



