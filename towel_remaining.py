import RPi.GPIO as GPIO
import time

# 사진에 명시된 핀 번호 (BCM 모드 기준 GPIO 번호 사용)
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
    # 트리거 핀으로 10us 펄스 전송
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    start_time = time.time()
    stop_time = time.time()

    # Echo 핀이 High가 될 때까지 대기 (시작 시간)
    timeout = time.time() + 0.05
    while GPIO.input(echo) == 0:
        start_time = time.time()
        if time.time() > timeout:
            return None

    # Echo 핀이 Low가 될 때까지 대기 (도착 시간)
    timeout = time.time() + 0.05
    while GPIO.input(echo) == 1:
        stop_time = time.time()
        if time.time() > timeout:
            return None

    # 시간 차이를 통해 거리 계산 (음속 34300 cm/s)
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2
    return distance

# ==========================================
# 새로 추가된 run() 함수!
# ==========================================
def run():
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
    except Exception as e:
        print(f"초음파 센서 에러: {e}")
    finally:
        GPIO.cleanup()


# 이 파일만 단독으로 실행할 때도 잘 동작하도록 유지
if __name__ == '__main__':
    run()
    import RPi.GPIO as GPIO
import time

# 사진에 명시된 핀 번호 (BCM 모드 기준 GPIO 번호 사용)
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
    # 트리거 핀으로 10us 펄스 전송
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    start_time = time.time()
    stop_time = time.time()

    # Echo 핀이 High가 될 때까지 대기 (시작 시간)
    timeout = time.time() + 0.05
    while GPIO.input(echo) == 0:
        start_time = time.time()
        if time.time() > timeout:
            return None

    # Echo 핀이 Low가 될 때까지 대기 (도착 시간)
    timeout = time.time() + 0.05
    while GPIO.input(echo) == 1:
        stop_time = time.time()
        if time.time() > timeout:
            return None

    # 시간 차이를 통해 거리 계산 (음속 34300 cm/s)
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2
    return distance

# ==========================================
# 새로 추가된 run() 함수!
# ==========================================
def run():
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
    except Exception as e:
        print(f"초음파 센서 에러: {e}")
    finally:
        GPIO.cleanup()


# 이 파일만 단독으로 실행할 때도 잘 동작하도록 유지
if __name__ == '__main__':
    run()