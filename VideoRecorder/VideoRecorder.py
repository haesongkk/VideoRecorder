import cv2

#URL = "rtsp://210.99.70.120:1935/live/cctv032.stream"
#URL = "rtmp://210.99.70.120/live/cctv032.stream"
URL = "http://210.99.70.120:1935/live/cctv032.stream/playlist.m3u8"

# VideoCapture 객체 생성
video = cv2.VideoCapture(URL)
if not video.isOpened():
    print("비디오가 열리지 않습니다.")
    exit()

while True:

    # 최신 프레임을 받아온다
    valid, frame = video.read()
    if not valid:
        print("프레임을 읽을 수 없습니다.")
        break

    # 현재 프레임 띄우기
    cv2.imshow('Video Stream', frame)

    # ESC 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == 27:
        break

# 자원 해제
video.release()
cv2.destroyAllWindows()
