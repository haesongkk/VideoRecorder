from tkinter import TRUE
import cv2
from datetime import datetime


def CreateVC(url):

     vc = cv2.VideoCapture(url)
     if not vc.isOpened():
         raise RuntimeError("VideoCapture 초기화 실패")

     return vc


def DestroyVC(vc):

    if vc is not None:
           vc.release()

    return None            


def CreateVW(vc):

    # 파일명 설정
    filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    # 코덱 설정
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # 프레임 크기 및 FPS 설정
    fps = int(vc.get(cv2.CAP_PROP_FPS))
    frame_width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # FPS와 해상도가 0이면 기본값 설정
    if frame_width == 0 or frame_height == 0:
        frame_width, frame_height = 640,480
    if fps <= 0 or fps > 60:
        fps = 30

    # VideoWriter 객체 생성
    vw = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))

    if not vw.isOpened():
        raise RuntimeError("VideoWriter 초기화 실패")

    return vw


def DestroyVW(vw):

    if vw is not None:
            vw.release()
    
    return None            


# main

url = "http://210.99.70.120:1935/live/cctv032.stream/playlist.m3u8"
vc = CreateVC(url)
vw = None
recording = False

while True:

    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        break

    if key == 32: 
        recording = not recording
        if recording:
            vw = CreateVW(vc)
        else :
            vw = DestroyVW(vw)


    valid, frame = vc.read()
    if not valid:
        raise RuntimeError("프레임을 읽을 수 없습니다.")

    if recording:
        vw.write(frame)
        cv2.putText(frame, "recording..", (20, 40),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('Video Stream', frame)


DestroyVC(vc)
DestroyVW(vw)
cv2.destroyAllWindows()

