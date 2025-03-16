import cv2
from datetime import datetime

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

# 코덱 설정
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# 녹화 상태 변수
recording = False  

# VideoWriter 객체
video_writer = None  

# 녹화 시작 시간
record_start_time = None  

# 프레임 카운트 (깜빡임 효과)
frame_count = 0  

print("Space 키: 녹화 시작/중지 | ESC 키: 종료")

while True:

    # 최신 프레임을 받아온다
    valid, frame = video.read()
    if not valid:
        print("프레임을 읽을 수 없습니다.")
        break
        
    # 녹화 중이면 비디오 저장
    if recording and video_writer is not None:
        video_writer.write(frame)

        elapsed_time = int((datetime.now() - record_start_time).total_seconds())
        time_text = f"{elapsed_time // 60:02}:{elapsed_time % 60:02}"  
        cv2.putText(frame, time_text, (80, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if (frame_count // fps) % 2 == 0:  
            cv2.circle(frame, (50, 50), 10, (0, 0, 255), -1)

    # 프레임 카운트 증가 (깜빡임 효과)
    frame_count += 1

    # 현재 프레임 띄우기
    cv2.imshow('Video Stream', frame)

    # 키 입력 받기
    key = cv2.waitKey(1) & 0xFF

    # ESC 키를 누르면 종료
    if key == 27:
        break

    # Space 키를 누르면 녹화 시작/중지
    if key == 32: 
        if not recording:
            recording = True
            # 녹화 시작 시간 저장
            record_start_time = datetime.now()  
            # 파일명 설정
            output_filename = f"video_{record_start_time.strftime('%Y%m%d_%H%M%S')}.mp4"
            # VideoWriter 객체 생성
            video_writer = cv2.VideoWriter(output_filename, fourcc, fps, (frame_width, frame_height))
        else:
            recording = False
             # VideoWriter 객체 해제
            video_writer.release() 
            video_writer = None

# 자원 해제
video.release()
if video_writer is not None:
    video_writer.release()
cv2.destroyAllWindows()
