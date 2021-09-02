import datetime
import sqlite3
import os
import errno


# DBlog : log 발생상황에 대한 DB 처리 클래스
class DBlog:
    # __int__ : 생성자
    # 파라미터(camnum, time, path, situation)
    # camnum:발생한 카메라
    # situation:발생상황 종류
    # time=발생 시간
    # path:스크린샷 저장 경로
    def __init__(self, camnum=None, time=None, path=None,situation=None):
        self.now = time
        self.situation = situation
        self.camnum = camnum
        self.path = path
        self.connectdb()

    # connectdb(): DB파일 선언 및 테이블 없을 경우 테이블 생성 함수
    def connectdb(self):
        # 파일 경로 생성, db 폴더가 존재 하지 않을 경우 예외처리 하여 파일 경로 생성
        try:
            if not (os.path.isdir("./db")):
                os.makedirs(os.path.join("./db"))
        except OSError as e:  # 생성 실패 시 오류 코드 출력
            if e.errno != errno.EEXIST:
                print("Dir error")
            raise
        # DB 파일 연결 및 커서 초기화
        self.conn = sqlite3.connect('./db/log.db')
        self.cur = self.conn.cursor()
        # 입력받은 상황에 대한 테이블이 존재하는지 판단하고 존재하지 않을 경우
        # (날짜, 상황번호, 카메라번호, 스크린샷경로)로 log_(상황번호)의 테이블 생성
        self.cur.execute("CREATE TABLE IF NOT EXISTS log_" + str(self.situation) +
                         " (day INTEGER, situation INTEGER, camera INTEGER, screenshot_address TEXT)")
        self.conn.commit()

    # closedb(): DB 종료 함수, 종료 시 저장기한 확인 수행
    def closedb(self):
        #DB를 종료할 때 저장기한이 만료된 데이터가 있는지 판단하여 삭제
        self.delrecord()
        self.conn.commit()
        self.conn.close()

    # makerecord() : 입력받은 정보를 상황에 해당하는 테이블에 레코드로 추가하는 함수
    def makerecord(self):
        self.conn.execute("INSERT INTO log_" + str(self.situation) + " VALUES(?,?,?,?)",
                      (self.now.strftime('%Y%m%d%H%M%S'), self.situation ,self.camnum, self.path))

        self.conn.commit()

    # findrecord() : 레코드 검색 함수
    # 파라미터: (cam, situation, day)
    # cam:발생한 카메라
    # situation:발생상황 종류
    # day=발생 시간 ex)20210101
    def findrecord(self, cam, situation, day): # 레코드 검색 함수
        #테이블 존재 여부 확인
        self.cur.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE name='log_{str(situation)}'")
        if self.cur.fetchone()[0] == 1:
            # 입력받은 상황, 카메라번호, 일자에 해당하는 레코드 검색
            day = str(day) + '%'
            self.cur.execute("SELECT * FROM log_" + str(situation) + " WHERE camera=" + str(cam) + " AND day LIKE '%s'"%str(day))
            try:
                path = self.cur.fetchone()[2]
            # path가 없을 경우 빈 문자열 반환(상위 레벨에서 비어있을 경우에 해당하는 처리 필요)
            except TypeError:
                path = ''
        else:
            path = ''
        self.conn.commit()
        # 해당 동영상 파일의 경로 반환
        return path

    # delrecord(): 저장기한 만료된 스크린샷에 대한 DB 처리 및 삭제 함수
    def delrecord(self):
        time = datetime.datetime.now()
        # 저장기한 10주로 설정
        lastday = time - datetime.timedelta(weeks=10)
        # 삭제 일자에 해당하는 레코드 탐색
        while True:
            delpictime = lastday.strftime('%Y%m%d') + '%'
            self.cur.execute("SELECT * FROM log_" + str(self.situation) + " WHERE day LIKE '%s'"%str(delpictime))
            dellist = self.cur.fetchone()
            try:
                path = dellist[2]
            # path가 없을 경우 더이상 삭제할 스크린샷이 없다 판단하여 반복문 탈출
            except TypeError:
                break
            # 찾은 path의 파일 삭제 및 DB 레코드 삭제
            if os.path.isfile(path):
                os.remove(path)
            self.conn.execute("DELETE FROM log_" + str(self.situation) + " WHERE day LIKE '%s'"%str(delpictime))
            self.conn.commit()
        self.conn.commit()