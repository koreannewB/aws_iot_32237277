import time
import state

SENSORS = {
    1: {"trig": 23, "echo": 24},
    2: {"trig": 25, "echo": 8},
}

MIN_DIST_CM = 5.0
MAX_DIST_CM = 30.0
SPEED_OF_SOUND = 34300
MEASURE_INTERVAL = 1.0


def _measure_distance_cm(gpio, trig, echo):
    gpio.output(trig, True)
    time.sleep(0.00001)
    gpio.output(trig, False)

    timeout = time.time() + 0.05
    start = time.time()
    while gpio.input(echo) == 0:
        start = time.time()
        if time.time() > timeout:
            return None

    timeout = time.time() + 0.05
    end = time.time()
    while gpio.input(echo) == 1:
        end = time.time()
        if time.time() > timeout:
            return None

    return (end - start) * SPEED_OF_SOUND / 2


def _dist_to_count(distance_cm, max_count):
    clamped = max(MIN_DIST_CM, min(MAX_DIST_CM, distance_cm))
    ratio = (MAX_DIST_CM - clamped) / (MAX_DIST_CM - MIN_DIST_CM)
    return round(ratio * max_count)


def run():
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        for pins in SENSORS.values():
            GPIO.setup(pins["trig"], GPIO.OUT)
            GPIO.setup(pins["echo"], GPIO.IN)
            GPIO.output(pins["trig"], False)
        time.sleep(0.5)

        print("[towel] 초음파 센서 초기화 완료")

        while True:
            for rack_id, pins in SENSORS.items():
                dist = _measure_distance_cm(GPIO, pins["trig"], pins["echo"])
                if dist is None:
                    print(f"[towel] {rack_id}번 비치대 측정 타임아웃")
                    continue
                max_count = state.TOWEL[rack_id]["max"]
                count = _dist_to_count(dist, max_count)
                state.TOWEL[rack_id]["count"] = count
                print(f"[towel] {rack_id}번 비치대: {dist:.1f}cm → {count}/{max_count}장")
            time.sleep(MEASURE_INTERVAL)

    except ImportError:
        print("[towel] RPi.GPIO 없음 - 더미 모드 실행 (PC 테스트용)")
        _run_dummy()


def _run_dummy():
    import math
    t = 0.0
    while True:
        for rack_id in state.TOWEL:
            max_c = state.TOWEL[rack_id]["max"]
            ratio = (math.sin(t + rack_id * 1.5) + 1) / 2
            state.TOWEL[rack_id]["count"] = round(ratio * max_c)
        t += 0.05
        time.sleep(MEASURE_INTERVAL)