import cv2
import sys
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui

class ShowVideo(QtCore.QObject):

    # pyqtSignal은 사용자가 정하는 시그널이라던데,,,
    VideoSignal = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, id = 0, parent=None):
        super(ShowVideo, self).__init__(parent)
        self.id = id
        self.camera = cv2.VideoCapture(self.id)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)

    @QtCore.pyqtSlot()
    def startVideo(self):
        global image

        ret, image = self.camera.read()
        self.height, self.width = image.shape[:2]   # 영상 사이즈

        run_video = True
        while run_video:
            ret, image = self.camera.read()

            # 출력 형태 결정
            color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            qt_image1 = QtGui.QImage(color_swapped_image.data,
                                    self.width,
                                    self.height,
                                    color_swapped_image.strides[0],
                                    QtGui.QImage.Format_RGB888)
            self.VideoSignal.emit(qt_image1)    # 시그널 보내기,,,?

            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(25, loop.quit) #25 ms
            loop.exec_()

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
        painter.drawImage((self.width()-self.image.width())/2, (self.height()-self.image.height())/2, self.image)
        self.image = QtGui.QImage()

    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")

        self.image = image
        if image.size() != self.size():
            self.setFixedSize(QtCore.QSize(853, 480))
        self.update()