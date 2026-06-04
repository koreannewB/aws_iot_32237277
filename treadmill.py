import time
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import state
from ultralytics import YOLO
import cv2
import base64
current_frame = None
model = YOLO('iotsmart_gym.pt')

ZONES = {
    1: (0,    0,    480,  1080),  # (x1, y1, x2, y2)
    2: (480,  0,    960,  1080),
    3: (960,  0,    1440, 1080),
    4: (1440, 0,    1920, 1080),
}

def is_person_in_zone(box, zone):
    x1, y1, x2, y2 = box          # YOLO: x1,y1,x2,y2
    zx1, zy1, zx2, zy2 = zone     # ZONES도 같은 순서여야 함
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    return zx1 < cx < zx2 and zy1 < cy < zy2
def trail_detect_run():
    global current_frame
    print("런닝머신감지기능작동")
    # cap = cv2.VideoCapture("ex1.mp4")
    USE_CAMERA = True 
    if USE_CAMERA:
        from picamera2 import Picamera2
        picam2 = Picamera2()
        picam2.start()
    else:
        cap = cv2.VideoCapture("iottest2.mp4")
    prev_detected = {1: False, 2: False, 3: False, 4: False}

    while True:
        if USE_CAMERA:
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        else:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                continue
        results = model(frame, verbose=False)
        annotated = results[0].plot()

        # 구역 경계선 (x축으로 4등분, 높이 1080)
        for x in [480, 960, 1440]:
            cv2.line(annotated, (x, 0), (x, 1080), (0, 255, 0), 3)

        annotated = cv2.resize(annotated, (640, 360))  # ✅ (width, height) 순서
        _, buffer = cv2.imencode('.jpg', annotated)
        current_frame = base64.b64encode(buffer).decode('utf-8')
        # print(f"프레임 저장됨: {len(current_frame)}")
        # YOLO 감지
       

        
        
 

        # 구역별 감지
        detected = {1: False, 2: False, 3: False, 4: False}
        for result in results:
            for box in result.boxes:
                if int(box.cls) == 0:  # person
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    for zone_id, zone in ZONES.items():
                        if is_person_in_zone((x1, y1, x2, y2), zone):
                            detected[zone_id] = True
                            print(f"{zone_id}번 런닝머신 사람 감지!")

        # state 업데이트
        for i in range(1, 5):
            if detected[i] != prev_detected[i]:  # 상태 변했을 때만
                if detected[i]:
                    print(f"{i}번 런닝머신 사람 등장!")
                else:
                    print(f"{i}번 런닝머신 사람 퇴장!")

            if detected[i]:
                state.TREADMILL[i] = "/static/img/onhuman.png"
            else:
                state.TREADMILL[i] = "/static/img/offhuman.png"

        prev_detected = detected.copy()




        # print("변경")