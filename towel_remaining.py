import RPi.GPIO as GPIO
import time
import state  # <-- 추가: 웹서버와 상태를 공유하기 위해 가져옵니다.

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

def run():
    try:
        setup_ultrasonic()
        while True:
            for name, pins in ULTRASONIC_SENSORS.items():
                dist = measure_distance(pins["trig"], pins["echo"])
                if dist is not None:
                    print(f"[{name}] 거리: {dist:.2f} cm")
                    
                    # --- [추가된 로직] state.TOWEL 실시간 업데이트 ---
                    sensor_id = int(name.split("_")[1]) # sensor_1 이면 숫자 1 추출
                    
                    if sensor_id in state.TOWEL:
                        # [주의] 이 부분은 거리에 따라 수건 갯수를 계산하는 식입니다.
                        # 예시: 수건 두께를 2cm로 가정 (거리가 가까울수록 수건이 많음)
                        # 실제 센서 설치 높이에 맞게 식을 수정해서 사용하세요!
                        calculated_count = state.TOWEL[sensor_id]["max"] - int(dist / 2)
                        
                        # 수건이 0장 미만으로 떨어지지 않도록 처리
                        calculated_count = max(0, calculated_count)
                        
                        # state.py 파일에 반영
                        state.TOWEL[sensor_id]["count"] = calculated_count
                    # ------------------------------------------------
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

if __name__ == '__main__':
    run()