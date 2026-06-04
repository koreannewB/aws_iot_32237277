import RPi.GPIO as GPIO
import time
import state

ULTRASONIC_SENSORS = {
    "sensor_1": {"trig": 23, "echo": 24, "towel_id": 1},
    "sensor_2": {"trig": 25, "echo": 8,  "towel_id": 2},
    "sensor_3": {"trig": 9,  "echo": 11, "towel_id": 3},
}

# 거리(cm) → 수건 잔량 변환
# 센서가 가까울수록 수건 많음 (쌓인 높이)
EMPTY_DIST  = 30.0  # 수건 없을 때 거리 (cm) → 실측으로 조정
FULL_DIST   =  5.0  # 수건 가득일 때 거리 (cm) → 실측으로 조정

def dist_to_count(dist, max_count):
    """거리 → 수건 개수로 변환"""
    dist = max(FULL_DIST, min(EMPTY_DIST, dist))  # 범위 클램핑
    ratio = (EMPTY_DIST - dist) / (EMPTY_DIST - FULL_DIST)
    return round(ratio * max_count)

def setup_ultrasonic():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for name, pins in ULTRASONIC_SENSORS.items():
        GPIO.setup(pins["trig"], GPIO.OUT)
        GPIO.setup(pins["echo"], GPIO.IN)
        GPIO.output(pins["trig"], False)
    print("[Towel] Ultrasonic sensors initialized")
    time.sleep(2)

def measure_distance(trig, echo):
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    start_time = time.time()
    stop_time  = time.time()

    timeout = time.time() + 0.05
    while GPIO.input(echo) == 0:
        start_time = time.time()
        if time.time() > timeout:
            return None

    timeout = time.time() + 0.05
    while GPIO.input(echo) == 1:
        stop_time = time.time()
        if time.time() > timeout:
            return None

    return (stop_time - start_time) * 34300 / 2

def run():
    try:
        setup_ultrasonic()
        while True:
            for name, pins in ULTRASONIC_SENSORS.items():
                dist = measure_distance(pins["trig"], pins["echo"])
                towel_id = pins["towel_id"]

                if dist is not None:
                    print(f"[Towel] {name} dist={dist:.2f}cm")
                    # state.TOWEL에 반영
                    if towel_id in state.TOWEL:
                        max_count = state.TOWEL[towel_id]["max"]
                        state.TOWEL[towel_id]["count"] = dist_to_count(dist, max_count)
                else:
                    print(f"[Towel] {name} timeout")

            time.sleep(1)

    except KeyboardInterrupt:
        print("[Towel] Stopped")
    except Exception as e:
        print(f"[Towel] Error: {e}")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    run()