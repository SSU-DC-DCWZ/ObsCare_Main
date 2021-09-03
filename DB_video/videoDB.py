import datetime
import sqlite3
import os
import errno

# DBvideo : 저장된 video 대한 DB 처리 클래스
class DBvideo:
    # __int__ : 생성자
    # camnum:발생한 카메라
    # time=발생 시간
    # path:스크린샷 저장 경로
    def __init__(self, camnum=None, time=None, path=None):
        self.now = time
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
        self.conn = sqlite3.connect('./db/video.db')
        self.cur = self.conn.cursor()
        # 입력받은 카메라 번호 대한 테이블이 존재하는지 판단하고 존재하지 않을 경우
        # (날짜, 동영상 경로)로 video_(카메라번호)의 테이블 생성
        self.cur.execute("CREATE TABLE IF NOT EXISTS video_" + str(self.camnum) + " (day INTEGER, video_address TEXT)")
        self.conn.commit()

    # makerecord() : 입력받은 정보를 상황에 해당하는 테이블에 레코드로 추가하는 함수
    def makerecord(self):
        self.conn.execute("INSERT INTO video_" + str(self.camnum) + " VALUES(?,?)", (self.now.strftime('%Y%m%d'), self.path))
        # 레코드 생성할 때는 일자가 바뀌었다는 뜻이므로 동시에 레코드 삭제 수행
        self.delrecord()
        self.conn.commit()

    # findrecord() : 레코드 검색 함수
    # cam:발생한 카메라
    # day=발생 시간 ex)20210101
    def findrecord(self, cam, day):
        #테이블 존재 여부 확인
        self.cur.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE name='video_{str(cam)}'")
        if self.cur.fetchone()[0] == 1:
            # 입력받은 일자에 해당하는 레코드 검색
            self.cur.execute("SELECT * FROM video_" + str(cam) + " WHERE day=" + str(day))
            try:
                path = self.cur.fetchone()[1]
            # path가 없을 경우 빈 문자열 반환(상위 레벨에서 비어있을 경우에 해당하는 처리 필요)
            except TypeError:
                path = ''
        else:
            path = ''
        self.conn.commit()
        # 해당 동영상 파일의 경로 반환
        return path

    # delrecord(): 저장기한 만료된 영상에 대한 DB 처리 및 삭제 함수
    def delrecord(self):
        # 저장기한 10주로 설정
        lastday = self.now - datetime.timedelta(weeks=10)
        # 삭제 일자에 해당하는 레코드 탐색
        self.cur.execute("SELECT * FROM video_" + str(self.camnum) + " WHERE day=" + lastday.strftime('%Y%m%d'))
        try:
            path = self.cur.fetchone()[1]
        # path가 없을 경우 빈 문자열 반환(상위 레벨에서 비어있을 경우에 해당하는 처리 필요)
        except TypeError:
            path = ''
        # 찾은 path의 파일 삭제 및 DB 레코드 삭제
        if os.path.isfile(path):
            os.remove(path)
        self.conn.execute("DELETE FROM video_" + str(self.camnum) + " WHERE day=" + lastday.strftime('%Y%m%d'))
        self.conn.commit()

    # closedb(): DB 종료 함수
    def closedb(self):
        self.conn.commit()
        self.conn.close()

