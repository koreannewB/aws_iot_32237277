import RPi.GPIO as GPIO
import time

ULTRASONIC_SENSORS = {
    "sensor_1": {"trig": 23, "echo": 24},
    "sensor_2": {"trig": 25, "echo": 8},
    "sensor_3": {"trig": 9,  "echo": 11},
}

def setup_ultrasonic():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for name, pins in ULTRASONIC_SENSORS.items():
        GPIO.setup(pins["trig"], GPIO.OUT)
        GPIO.setup(pins["echo"], GPIO.IN)
        GPIO.output(pins["trig"], False)
    print("초음파 센서 초기화 완료. 안정화 대기 중...")
    time.sleep(2)

def measure_distance(trig, echo):
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    start_time = time.time()
    stop_time = time.time()

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

    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2
    return distance

# === 여기서부터가 실제로 프로그램을 돌리는 가장 중요한 부분입니다 ===
if __name__ == '__main__':
    try:
        setup_ultrasonic()
        while True:
            for name, pins in ULTRASONIC_SENSORS.items():
                dist = measure_distance(pins["trig"], pins["echo"])
                if dist is not None:
                    print(f"[{name}] 거리: {dist:.2f} cm")
                else:
                    print(f"[{name}] 측정 실패 (타임아웃)")
            print("-" * 30)
            time.sleep(1)
    except KeyboardInterrupt:
        print("측정 종료")
    finally:
        GPIO.cleanup()
