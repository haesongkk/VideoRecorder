import cv2
import numpy as np
from datetime import datetime

url = "http://210.99.70.120:1935/live/cctv032.stream/playlist.m3u8"
videoextension = ".mp4"
videocodec = 'mp4v'

mainwindowname = "Video Recorder"
recordgingtxt = "recording.."

subwindowname = "Zoom"
zoomsize = 100 
zoommagnification = 2 

class MouseHandler:

    def __init__(self, _winName):
        self.winName = _winName
        self.x = 0
        self.y = 0

        cv2.namedWindow(self.winName)
        cv2.setMouseCallback(self.winName, self.Update)

    def Update(self, _event, _x, _y, _flags, _param):
        if _event == cv2.EVENT_MOUSEMOVE:
            self.x, self.y = _x, _y  

    def GetMousePos(self):
        return self.x, self.y


def CreateVC(url):
    return cv2.VideoCapture(url)

def DestroyVC(vc):
    if vc is not None:
        vc.release()

def CreateVW(_fps, _width, _height):
    filename = f"vr_{datetime.now().strftime('%Y%m%d_%H%M%S')}{videoextension}"
    fourcc = cv2.VideoWriter_fourcc(*videocodec)

    if _width == 0 or _height == 0:
        _width, _height = 640, 480
    if _fps <= 0 or _fps > 60:
        _fps = 30

    return cv2.VideoWriter(filename, fourcc, _fps, (_width, _height))

def DestroyVW(vw):
    if vw is not None:
        vw.release()
    return None

def ProcessRecord(_videoRecorder, _image):
    _videoRecorder.write(_image)
    cv2.putText(_image, recordgingtxt, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

def ProcessZoom(_mouseHandler, _image):
     mousePosX, mousePosY = _mouseHandler.GetMousePos()
     x1 = max(min(mousePosX - zoomsize // 2, _image.shape[1] -zoomsize), 0)
     y1 = max(min(mousePosY - zoomsize // 2, _image.shape[0] - zoomsize), 0)
     x2, y2 = x1 + zoomsize, y1 + zoomsize
     zoom_region = _image[y1:y2, x1:x2]

     if zoom_region.size > 0:
         zoom_region = cv2.resize(zoom_region, (zoomsize *zoommagnification, zoomsize * zoommagnification),interpolation=cv2.INTER_LINEAR)

     return zoom_region

# main

vc = CreateVC(url)
vw = None
mouseHandler = MouseHandler(mainwindowname)
recording = False

while True:
    key = cv2.waitKey(1) & 0xFF

     # ESC 입력 : 종료
    if key == 27: 
        break

    # Space 입력 : 녹화 시작/중지
    if key == 32:  
        recording = not recording
        if recording:
            vw = CreateVW(int(vc.get(cv2.CAP_PROP_FPS)), int(vc.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        elif vw is not None:
            vw = DestroyVW(vw)
    
    tmp, image = vc.read()

    # 저장
    if recording:
        ProcessRecord(vw, image)
    
    # 도움말과 함께 영상 출력
    cv2.putText(image, "Press SPACE to Start/Stop Recording", (20, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.imshow(mainwindowname, image)

    # zoom 화면 계산 및 출력
    zoomImg = ProcessZoom(mouseHandler, image)
    cv2.imshow(subwindowname, zoomImg)

# 프로그램 종료
DestroyVC(vc)
DestroyVW(vw)
cv2.destroyAllWindows()