import datetime
import sqlite3
import os
import errno

# 영상에 대한 DB 처리 클래스
class DBvideo:
    def __init__(self, num, time, path=None): # num=DB 작업할 카메라 번호, time=datetime.datetime.now(), path=동영상의 절대 경로
        self.now = time
        self.camnum = num
        self.path = path
        if self.path == None: # 검색기능의 클래스 선언에서는 path 인자 없음
                self.findtime = time
                self.findnum = num
        self.connectdb()

    def __del__(self):
        pass

    def connectdb(self): # DB파일 선언 및 테이블 없을 경우 테이블 생성하는 함수
        try:  # 파일 경로 생성, 경로가 존재 하지 않을 경우 파일 경로 생성
            if not (os.path.isdir("./db")):
                os.makedirs(os.path.join("./db"))
        except OSError as e:  # 생성 실패 시 오류 코드 출력
            if e.errno != errno.EEXIST:
                print("Dir error")
            raise
        self.conn = sqlite3.connect('./db/video.db')
        self.cur = self.conn.cursor()
        # 카메라 별로 별도의 테이블 생성
        self.cur.execute("CREATE TABLE IF NOT EXISTS video_" + str(self.camnum) + " (day INTEGER, video_address TEXT)")
        self.conn.commit()

    def makerecord(self): #레코드(TIME, PATH)생성 함수
        self.conn.execute("INSERT INTO video_" + str(self.camnum) + " VALUES(?,?)", (self.now.strftime('%Y%m%d'), self.path))
        self.conn.commit()
        self.delrecord() # 레코드 생성할 때는 일자가 바뀌었다는 뜻이므로 동시에 레코드 삭제 수행
        self.conn.close()

    def findrecord(self,cam,day): # 레코드 검색 함수
        # 입력받은 일자에 해당하는 레코드 검색
        self.cur.execute("SELECT * FROM video_" + str(cam) + " WHERE day=" + str(day))
        try:
            path = self.cur.fetchone()[1]
        except TypeError: # path가 없을 경우 빈 문자열 반환(상위 레벨에서 비어있을 경우에 해당하는 처리 필요)
            path = ''
        self.closedb()
        return path # 해당 동영상 파일의 경로 반환

    # 해당 동영상 파일의 경로 반환

    def delrecord(self): # 저장기한 만료된 영상에 대한 DB 처리 및 삭제 함수
        lastday = self.now - datetime.timedelta(weeks=10) #저장기한 10주로 설정
        self.cur.execute("SELECT * FROM video_" + str(self.camnum) + " WHERE day=" + lastday.strftime('%Y%m%d'))
        try:
            path = self.cur.fetchone()[1]
        except TypeError:  # path가 없을 경우 빈 문자열 반환(상위 레벨에서 비어있을 경우에 해당하는 처리 필요)
            path = ''
        if os.path.isfile(path):
            os.remove(path)
        self.conn.execute("DELETE FROM video_" + str(self.camnum) + " WHERE day=" + lastday.strftime('%Y%m%d'))
        self.conn.commit()

    def closedb(self): #  DB 종료 함수
        self.conn.commit()
        self.conn.close()

