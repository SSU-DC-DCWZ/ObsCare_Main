from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPalette
from PyQt5 import uic
from prev_playlist import CMultiMedia
import sys
import datetime
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
form = resource_path("prev_player.ui")

form_class = uic.loadUiType(form)[0]

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)


class CWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi(form, self)

        # Multimedia Object
        self.mp = CMultiMedia(self, self.view)

        # video background color
        pal = QPalette()
        pal.setColor(QPalette.Background, Qt.black)
        self.view.setAutoFillBackground(True)
        self.view.setPalette(pal)

        # volume, slider
        self.vol.setRange(0, 100)
        self.vol.setValue(50)

        # play time
        self.duration = ''

        # signal
        self.btn_add.clicked.connect(self.clickAdd)
        self.btn_del.clicked.connect(self.clickDel)
        self.btn_play.clicked.connect(self.clickPlay)
        self.btn_stop.clicked.connect(self.clickStop)
        self.btn_pause.clicked.connect(self.clickPause)
        self.btn_forward.clicked.connect(self.clickForward)
        self.btn_prev.clicked.connect(self.clickPrev)

        self.list.itemDoubleClicked.connect(self.dbClickList)
        self.vol.valueChanged.connect(self.volumeChanged)
        self.bar.sliderMoved.connect(self.barChanged)

    def clickAdd(self):
        files, ext = QFileDialog.getOpenFileNames(self
                                                  , 'Select one or more files to open'
                                                  , ''
                                                  , 'Video (*.mp4 *.mpg *.mpeg *.avi *.wma)')

        if files:
            cnt = len(files)
            row = self.list.count()
            for i in range(row, row + cnt):
                self.list.addItem(files[i - row])
            self.list.setCurrentRow(0)

            self.mp.addMedia(files)

    def clickDel(self):
        row = self.list.currentRow()
        self.list.takeItem(row)
        self.mp.delMedia(row)

    def clickPlay(self):
        index = self.list.currentRow()
        self.mp.playMedia(index)

    def clickStop(self):
        self.mp.stopMedia()

    def clickPause(self):
        self.mp.pauseMedia()

    def clickForward(self):
        cnt = self.list.count()
        curr = self.list.currentRow()
        if curr < cnt - 1:
            self.list.setCurrentRow(curr + 1)
            self.mp.forwardMedia()
        else:
            self.list.setCurrentRow(0)
            self.mp.forwardMedia(end=True)

    def clickPrev(self):
        cnt = self.list.count()
        curr = self.list.currentRow()
        if curr == 0:
            self.list.setCurrentRow(cnt - 1)
            self.mp.prevMedia(begin=True)
        else:
            self.list.setCurrentRow(curr - 1)
            self.mp.prevMedia()

    def dbClickList(self, item):
        row = self.list.row(item)
        self.mp.playMedia(row)

    def volumeChanged(self, vol):
        self.mp.volumeMedia(vol)

    def barChanged(self, pos):
        print(pos)
        self.mp.posMoveMedia(pos)

    def updateState(self, msg):
        self.state.setText(msg)

    def updateBar(self, duration):
        self.bar.setRange(0, duration)
        self.bar.setSingleStep(int(duration / 10))
        self.bar.setPageStep(int(duration / 10))
        self.bar.setTickInterval(int(duration / 10))
        td = datetime.timedelta(milliseconds=duration)
        stime = str(td)
        idx = stime.rfind('.')
        self.duration = stime[:idx]

    def updatePos(self, pos):
        self.bar.setValue(pos)
        td = datetime.timedelta(milliseconds=pos)
        stime = str(td)
        idx = stime.rfind('.')
        stime = f'{stime[:idx]} / {self.duration}'
        self.playtime.setText(stime)


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     w = CWidget()
#     w.show()
#     sys.exit(app.exec_())