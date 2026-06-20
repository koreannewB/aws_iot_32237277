import time
import state
import cv2
import base64

current_frame = None
USE_FAKE_DETECTION = True


def trail_detect_run():
    global current_frame
    print("[Treadmill] Detection started")

    USE_CAMERA = False
    if USE_CAMERA:
        from picamera2 import Picamera2
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(
            main={"size": (1920, 1080), "format": "RGB888"}
        )
        picam2.configure(config)
        picam2.start()
    else:
        cap = cv2.VideoCapture("awssmart.mp4")
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

        annotated = frame.copy()

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
        t = int(time.time()) % 20

        detected = {
            1: True,
            2: t < 10,
            3: False,
            4: t >= 10
        }

        # state 업데이트
        for i in range(1, 5):
            if detected[i] != prev_detected[i]:
                print(f"[Treadmill] #{i} {'entered' if detected[i] else 'left'}")
            state.TREADMILL[i] = "/static/img/onhuman.png" if detected[i] else "/static/img/offhuman.png"

        prev_detected = detected.copy()