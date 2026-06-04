import time
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import state
from ultralytics import YOLO
import cv2
import base64

current_frame = None
model = YOLO('iotsmart_gym.pt')

def make_zones(w, h):
    """프레임 크기에 맞춰 자동 4등분"""
    step = w // 4
    return {
        1: (0,        0, step,     h),
        2: (step,     0, step * 2, h),
        3: (step * 2, 0, step * 3, h),
        4: (step * 3, 0, w,        h),
    }

def is_person_in_zone(box, zone):
    x1, y1, x2, y2 = box
    zx1, zy1, zx2, zy2 = zone
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    return zx1 < cx < zx2 and zy1 < cy < zy2

def trail_detect_run():
    global current_frame
    print("[Treadmill] Detection started")

    USE_CAMERA = True
    if USE_CAMERA:
        from picamera2 import Picamera2
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(
            main={"size": (1920, 1080), "format": "RGB888"}
        )
        picam2.configure(config)
        picam2.start()
    else:
        cap = cv2.VideoCapture("iottest2.mp4")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    prev_detected = {1: False, 2: False, 3: False, 4: False}
    ZONES = None  # 첫 프레임에서 자동 설정

    while True:
        if USE_CAMERA:
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        else:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

        h, w = frame.shape[:2]

        # 첫 프레임에서 ZONES 자동 설정
        if ZONES is None:
            ZONES = make_zones(w, h)
            print(f"[Treadmill] Frame size: {w}x{h}")
            print(f"[Treadmill] ZONES: {ZONES}")

        results = model(frame, verbose=False)
        annotated = results[0].plot()

        # 구역 경계선 + 번호 그리기
        step = w // 4
        for i, x in enumerate([step, step * 2, step * 3]):
            cv2.line(annotated, (x, 0), (x, h), (0, 255, 0), 3)
        for zone_id in range(1, 5):
            cx = (zone_id - 1) * step + step // 2
            cv2.putText(annotated, str(zone_id), (cx - 20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)

        annotated = cv2.resize(annotated, (640, 360))
        _, buffer = cv2.imencode('.jpg', annotated)
        current_frame = base64.b64encode(buffer).decode('utf-8')

        # 구역별 감지
        detected = {1: False, 2: False, 3: False, 4: False}
        for result in results:
            for box in result.boxes:
                if int(box.cls) == 0:  # person
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    for zone_id, zone in ZONES.items():
                        if is_person_in_zone((x1, y1, x2, y2), zone):
                            detected[zone_id] = True
                            print(f"[Treadmill] Zone {zone_id} occupied")

        # state 업데이트
        for i in range(1, 5):
            if detected[i] != prev_detected[i]:
                print(f"[Treadmill] #{i} {'entered' if detected[i] else 'left'}")
            state.TREADMILL[i] = "/static/img/onhuman.png" if detected[i] else "/static/img/offhuman.png"

        prev_detected = detected.copy()