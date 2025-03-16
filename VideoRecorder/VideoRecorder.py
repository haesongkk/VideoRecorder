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


def CreateVW(vc):
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

# 배경 차분기 사용 (MOG2) - 신호등 같은 정적인 물체를 배경으로 포함하도록 조정
fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)

frameCount = 0
 # 배경을 저장할 프레임 간격 (5초마다)
save_interval = 300 

while True:
    key = cv2.waitKey(1) & 0xFF

    # ESC 입력 : 종료
    if key == 27:  
        break

    # Space 입력 : 녹화 시작/중지
    if key == 32:  
        recording = not recording
        if recording:
            vw = CreateVW(vc)
        elif vw is not None:
            vw = DestroyVW(vw)

    valid, image = vc.read()
    if not valid:
        raise RuntimeError("이미지를 읽을 수 없습니다.")

    if recording:
        vw.write(image)
        cv2.putText(image, "recording..", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    frameCount += 1

    # 배경 차분 적용 (배경 업데이트 속도 조절)
    fg_mask = fgbg.apply(image, learningRate=0.001)

    # 노이즈 제거 (작은 객체 제거)
    fg_mask = cv2.medianBlur(fg_mask, 5)

    # 움직이는 객체(전경) 검출
    img_fore = cv2.bitwise_and(image, image, mask=fg_mask)

    # 배경을 어둡게 처리
    img_dark_background = image.copy()
    img_dark_background[fg_mask == 0] = (img_dark_background[fg_mask == 0] * 0.1).astype(np.uint8)  

    # 윤곽선 감지
    edges = cv2.Canny(fg_mask, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 윤곽선을 흰색(255, 255, 255)으로 강조
    img_edges = np.zeros_like(image)
    cv2.drawContours(img_edges, contours, -1, (255, 255, 255), 2) 

    # 배경이 어두운 원본 + 움직이는 객체 + 윤곽선 합성
    final_display = cv2.addWeighted(img_dark_background, 1.0, img_fore, 1.0, 0)
    final_display = cv2.add(final_display, img_edges)

    # 원본과 윤곽선 강조된 화면을 가로로 나란히 출력
    combined_display = np.hstack((image, final_display)) 

    cv2.imshow("Original | Object Detection", combined_display)

    # 배경을 주기적으로 저장 
    if frameCount % save_interval == 0:
        print(f"배경 업데이트: {frameCount} 프레임째 저장됨")
        cv2.imwrite("raw_back.png", fg_mask)

DestroyVC(vc)
DestroyVW(vw)
cv2.destroyAllWindows()
