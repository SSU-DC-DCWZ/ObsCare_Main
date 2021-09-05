# ObsCare_Main
## 소개
## 시스템 구성도
![image](https://user-images.githubusercontent.com/49185035/132118172-4c61f4bd-609e-4407-8e78-bbd160e2339e.png)
## 시연 화면
### 상황 감지 시 log 발생
![image](https://user-images.githubusercontent.com/49185035/132118122-bc0d449c-721b-45e6-a11f-87774ec60777.png)
### 이전 영상 확인 위한 정보 입력
![image](https://user-images.githubusercontent.com/49185035/132118151-9dede290-e0f5-4424-85ee-82c1560c30f1.png)
### 이전 영상 확인
![image](https://user-images.githubusercontent.com/49185035/132118157-ec7585ef-f9e0-4b69-bbdf-65bbdb7dc850.png)

## 설치 및 실행
``` python 
git clone https://github.com/SSU-DC-DCWZ/ObsCare_Main.git
pip install -r requirements.txt
```
``` python
python3 main.py
```


## 시연 시스템 사양
#### 1. UVC 카메라
국제에이브이 에이스원 X PRO2
#### 2. GPU 및 cuda 버전
NVIDIA GeForce RTX 3080 10GB, CUDA 11.4
#### 3. CPU
Intel(R) Core(TM) i9-10900K CPU @ 3.70GHz
#### 4. 메모리
16GB
## 개발 환경
#### Ubuntu 20.04.3 LTS (GNU/Linux 5.11.0-25-generic x86_64)
#### PyCharm 2021.1.13 (Professional Edition) @11.0.11
#### Visual Studio Code 1.60.0
## 기여자
#### **강병휘**([essentialhrdy](https://github.com/essentialhrdy)) : 모델 학습 및 Object Detection 처리
#### **이찬서**([Lfollow-CS](https://github.com/Lfollow-CS)) : DB,Stream 관리 및 개별 프로젝트 통합
#### **박세진**([pseeej](https://github.com/pseeej)) : UI 생성 및 Model 스레딩 관리
## 라이선스
#### 이 프로젝트는 [GNU General Public License v3.0](https://github.com/SSU-DC-DCWZ/ObsCare_Main/blob/main/LICENSE)을 사용합니다.

