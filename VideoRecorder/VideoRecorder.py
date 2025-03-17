import cv2
import numpy as np
from datetime import datetime

def CreateVC(url):
    vc = cv2.VideoCapture(url)
    if not vc.isOpened():
        raise RuntimeError("VideoCapture 초기화 실패")
    return vc

def DestroyVC(vc):
    if vc is not None:
        vc.release()

def CreateVW(vc, mode):
    filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    fps = int(vc.get(cv2.CAP_PROP_FPS))
    frame_width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if frame_width == 0 or frame_height == 0:
        frame_width, frame_height = 640, 480
    if fps <= 0 or fps > 60:
        fps = 30

    vw = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))

    if not vw.isOpened():
        raise RuntimeError("VideoWriter 초기화 실패")

    return vw

def DestroyVW(vw):
    if vw is not None:
        vw.release()
    return None

# 비디오 스트림 설정
url = "http://210.99.70.120:1935/live/cctv032.stream/playlist.m3u8"
vc = CreateVC(url)
vw = None
recording = False

# 0: 원본, 1: 객체 감지
mode = 0  
show_help = False

fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)
frameCount = 0
save_interval = 300

while True:
    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # ESC 입력 : 종료
        break

    if key == 32:  # Space 입력 : 녹화 시작/중지
        recording = not recording
        if recording:
            vw = CreateVW(vc, mode)
        elif vw is not None:
            vw = DestroyVW(vw)
    
    if key == ord('z'):  # z 입력 : 화면 모드 전환
        mode = 1 - mode
        print(f"모드 변경: {'객체 감지' if mode else '원본'}")
    
    if key == 9:  # TAB 키 입력 시 도움말 토글
        show_help = not show_help

    valid, image = vc.read()
    if not valid:
        raise RuntimeError("이미지를 읽을 수 없습니다.")

    frameCount += 1
    
    fg_mask = fgbg.apply(image, learningRate=0.001)
    fg_mask = cv2.medianBlur(fg_mask, 5)

    img_fore = cv2.bitwise_and(image, image, mask=fg_mask)
    img_dark_background = image.copy()
    img_dark_background[fg_mask == 0] = (img_dark_background[fg_mask == 0] * 0.1).astype(np.uint8)
    
    edges = cv2.Canny(fg_mask, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    img_edges = np.zeros_like(image)
    cv2.drawContours(img_edges, contours, -1, (255, 255, 255), 2)
    
    final_display = cv2.addWeighted(img_dark_background, 1.0, img_fore, 1.0, 0)
    final_display = cv2.add(final_display, img_edges)

    display_image = image if mode == 0 else final_display

    if recording:
        vw.write(display_image)
        cv2.putText(display_image, "recording..", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    if show_help:
        overlay = display_image.copy()
        cv2.rectangle(overlay, (50, 50), (600, 200), (0, 0, 0), -1)
        cv2.putText(overlay, "Controls:", (60, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(overlay, "ESC: Exit", (60, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(overlay, "SPACE: Start/Stop Recording", (60, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(overlay, "Z: Toggle Mode", (60, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        display_image = cv2.addWeighted(overlay, 0.7, display_image, 0.3, 0)
    
    cv2.putText(display_image, "Press TAB to Toggle Help", (20, display_image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    cv2.imshow("Video Feed", display_image)

    if frameCount % save_interval == 0:
        print(f"배경 업데이트: {frameCount} 프레임째 저장됨")
        cv2.imwrite("raw_back.png", fg_mask)

DestroyVC(vc)
DestroyVW(vw)
cv2.destroyAllWindows()