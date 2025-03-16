import cv2

URL = "http://210.99.70.120:1935/live/cctv032.stream/playlist.m3u8"

# VideoCapture 객체 생성
video = cv2.VideoCapture(URL)
if not video.isOpened():
    print("비디오가 열리지 않습니다.")
    exit()

# 프레임 크기 및 FPS 설정
frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(video.get(cv2.CAP_PROP_FPS))

# FPS와 해상도가 0이면 기본값 설정
if fps <= 0 or fps > 60:  
    fps = 30 
if frame_width == 0 or frame_height == 0:
    frame_width, frame_height = 640, 480  

# 출력 파일명과 코덱 설정
output_filename = "output.mp4" 
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# 녹화 상태 변수
recording = False  

# VideoWriter 객체
video_writer = None  

print("Space 키: 녹화 시작/중지 | ESC 키: 종료")

while True:

    # 최신 프레임을 받아온다
    valid, frame = video.read()
    if not valid:
        print("프레임을 읽을 수 없습니다.")
        break

    # 현재 프레임 띄우기
    cv2.imshow('Video Stream', frame)

    # 녹화 중이면 비디오 저장
    if recording and video_writer is not None:
        video_writer.write(frame)

    # 키 입력 받기
    key = cv2.waitKey(1) & 0xFF

    # ESC 키를 누르면 종료
    if key == 27:
        break

    # Space 키를 누르면 녹화 시작/중지
    if key == 32: 
        if not recording:
            print("녹화 시작!")
            recording = True
            # VideoWriter 객체 생성
            video_writer = cv2.VideoWriter(output_filename, fourcc, fps, (frame_width, frame_height))
        else:
            print("녹화 중지!")
            recording = False
             # VideoWriter 객체 해제
            video_writer.release() 
            video_writer = None

# 자원 해제
video.release()
if video_writer is not None:
    video_writer.release()
cv2.destroyAllWindows()
