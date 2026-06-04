import RPi.GPIO as GPIO
import time
import state

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
    # 초음파 발사 전 확실하게 핀을 끄고 안정화 (노이즈 방지)
    GPIO.output(trig, False)
    time.sleep(0.002)

    # 10us 펄스 전송
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    start_time = time.time()
    stop_time = time.time()

    # 타임아웃 제한 없이 Echo 핀이 High가 될 때까지 무한 대기
    while GPIO.input(echo) == 0:
        start_time = time.time()

    # 타임아웃 제한 없이 Echo 핀이 Low가 될 때까지 무한 대기
    while GPIO.input(echo) == 1:
        stop_time = time.time()

    # 시간 차이를 통해 거리 계산 (음속 34300 cm/s)
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2
    return distance

def run():
    try:
        setup_ultrasonic()
        while True:
            for name, pins in ULTRASONIC_SENSORS.items():
                dist = measure_distance(pins["trig"], pins["echo"])
                
                # 비정상적으로 튄 값(400cm 이상) 방어 로직 유지
                if dist > 400:
                    print(f"[{name}] 거리 비정상 튐: {dist:.2f} cm (무시됨)")
                else:
                    print(f"[{name}] 거리: {dist:.2f} cm")
                    
                    sensor_id = int(name.split("_")[1]) 
                    if sensor_id in state.TOWEL:
                        # 임시 수건 계산식
                        calculated_count = state.TOWEL[sensor_id]["max"] - int(dist / 2)
                        calculated_count = max(0, min(state.TOWEL[sensor_id]["max"], calculated_count))
                        
                        state.TOWEL[sensor_id]["count"] = calculated_count
                
                # 센서 간 간섭 방지를 위한 짧은 대기
                time.sleep(0.06) 
                
            print("-" * 30)
            
            # 전체 센서 1사이클 측정 후 대기
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("측정 종료")
    except Exception as e:
        print(f"초음파 센서 에러: {e}")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    run()