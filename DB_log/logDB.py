import datetime
import sqlite3
import os
import errno


#log 발생에 대한 DB 처리 클래스
class DBlog:
    def __init__(self, time, situation, camnum, path): #situation:발생상황, time=그떄의 시간, path:스크린샷 저장 경로
        self.now = time
        self.situation = situation
        self.camnum = camnum
        self.path = path
        self.connectdb()

    def __del__(self):
        self.closedb()  # 레코드 생성할 때는 일자가 바뀌었다는 뜻이므로 동시에 레코드 삭제 수행

    def connectdb(self): #DB파일 선언 및 테이블 없을 경우 테이블 생성하는 함수
        try:  # 파일 경로 생성, 경로가 존재 하지 않을 경우 파일 경로 생성
            if not (os.path.isdir("./db")):
                os.makedirs(os.path.join("./db"))
        except OSError as e:  # 생성 실패 시 오류 코드 출력
            if e.errno != errno.EEXIST:
                print("Dir error")
            raise
        self.conn = sqlite3.connect('./db/log.db')
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS log_" + str(self.situation) +
                                           " (day INTEGER, situation INTEGER, camera INTEGER, screenshot_address TEXT)")
        self.conn.commit()

    def closedb(self): #DB 종료 함수, 종료 시 저장기한 확인 수행
        self.delrecord()
        self.conn.commit()
        self.conn.close()

    def makerecord(self): #레코드(TIME, PATH)생성 함수
        self.conn.execute("INSERT INTO log_" + str(self.situation) + " VALUES(?,?,?,?)",
                      (self.now.strftime('%Y%m%d%H%M%S'), self.situation ,self.camnum, self.path))

        self.conn.commit()

    def delrecord(self): # 저장기한 만료된 스크린샷에 대한 DB 처리 및 삭제 함수
        time = datetime.datetime.now()
        lastday = time - datetime.timedelta(weeks=10) #저장기한 10주로 설정
        while True: #삭제 일자에 해당하는 레코드 탐색
            delpic = lastday.strftime('%Y%m%d') + '%'
            self.cur.execute("SELECT * FROM log_" + str(self.situation) + " WHERE day LIKE '%s'"%str(delpic))
            list = self.cur.fetchone()
            try:
                del_time = list[0]
                path = list[2]
            except TypeError:  # path가 없을 경우 더이상 삭제할 스크린샷이 없다 판단하여 반복문 탈출
                break
            if os.path.isfile(path):
                os.remove(path)
            self.conn.execute("DELETE FROM log_" + str(self.situation) + " WHERE day = " + str(del_time))
            self.conn.commit()
        self.conn.commit()