# ObsCare_Main
## 소개
#### 공공장소에서 눈만 돌리면 CCTV가 보인다는 말이 과언이 아닐 정도로 CCTV가 우리 생활에 깊숙이 자리 잡았습니다.
#### CCTV의 대수가 급격히 늘어나면서 관리와 효율성 문제와 더불어, 곳곳에 설치된 CCTV를 개별 관제하는 것으로는 응급 상황 대처 등에
#### 실효성이 떨어질 수 있다는 지적이 대두되고 있습니다.
#### 이런 문제점을 해결할 수 있는 방안으로 영상을 자동으로 분석하여
#### 문제 상황을 즉시 알리는 지능형 영상관제 시스템(ObsCare)을 제시하고자 합니다.

## 시스템 구성도
![image](https://user-images.githubusercontent.com/49185035/132118172-4c61f4bd-609e-4407-8e78-bbd160e2339e.png)

## 시연 영상
[![Video Label](https://user-images.githubusercontent.com/60226988/137311524-d325a2f5-e579-4a9d-8470-173a1f4ba58d.jpg)](https://www.youtube.com/watch?v=wJdjtgeti40)  
(클릭하면 유튜브 링크로 이동합니다)  

## 시연 화면
### 상황 감지 시 log 발생
![image](https://user-images.githubusercontent.com/49185035/132118122-bc0d449c-721b-45e6-a11f-87774ec60777.png)
### 이전 영상 확인 위한 정보 입력
![image](https://user-images.githubusercontent.com/49185035/132118151-9dede290-e0f5-4424-85ee-82c1560c30f1.png)
### 이전 영상 확인
![image](https://user-images.githubusercontent.com/49185035/132118157-ec7585ef-f9e0-4b69-bbdf-65bbdb7dc850.png)

## 설치 및 실행
#### Ubuntu 20.04 터미널에서 설치한다고 가정하였습니다.
### clone repository
``` 
git clone https://github.com/SSU-DC-DCWZ/ObsCare_Main.git
```

### 가상환경 생성 및 활성화
```
python -m venv venv
source venv/bin/activate
```

### 의존성 패키지 설치
```
cd ObsCare_Main
pip install torch==1.9.1+cu111 torchvision==0.10.0+cu111 -f https://download.pytorch.org/whl/torch_stable.html
pip install -r requirements.txt
```

### 실행
``` 
python3 ObsCare.py
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
#### 5. Python version
Python 3.8.10  

## 개발 환경
#### Ubuntu 20.04.3 LTS (GNU/Linux 5.11.0-25-generic x86_64)
#### PyCharm 2021.1.13 (Professional Edition) @11.0.11
#### Visual Studio Code 1.60.0

## 기여자
#### **강병휘**([essentialhrdy](https://github.com/essentialhrdy)) : 모델 학습 및 Object Detection 처리
#### **이찬서**([Lfollow-CS](https://github.com/Lfollow-CS)) : DB,Stream 관리 및 개별 프로젝트 통합
#### **박세진**([pseeej](https://github.com/pseeej)) : UI 생성 및 Model 스레딩 관리

## 라이브러리 라이선스
#### yolov5
Author : Glenn Jocher
License : GPLv3.0  
https://github.com/ultralytics/yolov5
#### Yolov5_DeepSort_Pytorch
Author : Mikel Broström
License : GPLv3.0  
https://github.com/mikel-brostrom/Yolov5_DeepSort_Pytorch
#### torch 1.9.1+cu111
License : BSD 3-clause  
https://github.com/intel/torch/blob/master/LICENSE.md
#### OpenCV 4.2.0.34
License : BSD 3-clause   
https://opencv.org/
#### PyQt5 5.15.4
License : GPLv3.0  
https://www.riverbankcomputing.com/software/pyqt/
#### openpyxl 3.0.7 
License : MIT/Expat  
https://openpyxl.readthedocs.io/en/stable/#
#### Pillow 8.3.1
License : PIL   
https://github.com/python-pillow/Pillow
#### PyYAML 5.4.1
License : MIT/  
https://github.com/yaml/pyyaml
#### scipy 1.7.0
License : liberal BSD  
https://www.scipy.org/index.html
#### tensorboard 2.5.0  
License : apache 2.0  
https://github.com/tensorflow/tensorboard/blob/master/LICENSE
#### tqdm 4.61.2   
License : MPL 2.0  
https://github.com/tqdm/tqdm/blob/master/LICENCE
#### seaborn 0.11.1    
License : BSD 3-clause  
https://github.com/mwaskom/seaborn/blob/master/LICENSE
#### pandas 1.3.0    
License : BSD 3-clause  
https://github.com/pandas-dev/pandas/blob/master/LICENSE
#### easydict 1.9    
License : GPLv3.0  
https://github.com/makinacorpus/easydict/blob/master/LICENSE
## 라이선스
#### 이 프로젝트는 [GNU General Public License v3.0](https://github.com/SSU-DC-DCWZ/ObsCare_Main/blob/main/LICENSE)을 사용합니다.
