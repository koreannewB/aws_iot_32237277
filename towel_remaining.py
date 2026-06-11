import RPi.GPIO as GPIO
import time
import state

ULTRASONIC_SENSORS = {
    "sensor_1": {"trig": 23, "echo": 24},
    "sensor_2": {"trig": 25, "echo": 8},
    "sensor_3": {"trig": 9,  "echo": 11},
}

FULL_TOWEL_DISTANCE_CM = 2.5
EMPTY_TOWEL_DISTANCE_CM = 15.0

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
    GPIO.output(trig, False)
    time.sleep(0.002)

    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    start_time = time.time()
    stop_time = time.time()

    # 타임아웃을 다시 추가하되, 시간을 0.1초로 넉넉하게 늘림
    timeout = time.time() + 0.1
    while GPIO.input(echo) == 0:
        start_time = time.time()
        if time.time() > timeout:
            return None

    timeout = time.time() + 0.1
    while GPIO.input(echo) == 1:
        stop_time = time.time()
        if time.time() > timeout:
            return None

    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2
    return distance

def distance_to_percent(distance_cm):
    if distance_cm <= FULL_TOWEL_DISTANCE_CM:
        return 100
    if distance_cm >= EMPTY_TOWEL_DISTANCE_CM:
        return 0

    usable_range = EMPTY_TOWEL_DISTANCE_CM - FULL_TOWEL_DISTANCE_CM
    percent = ((EMPTY_TOWEL_DISTANCE_CM - distance_cm) / usable_range) * 100
    return int(round(percent))

def run():
    try:
        setup_ultrasonic()
        while True:
            for name, pins in ULTRASONIC_SENSORS.items():
                dist = measure_distance(pins["trig"], pins["echo"])
                
                if dist is not None:
                    if dist > 400:
                        print(f"[{name}] 거리 비정상 튐: {dist:.2f} cm (무시됨)")
                    else:
                        print(f"[{name}] 거리: {dist:.2f} cm")
                        
                        sensor_id = int(name.split("_")[1]) 
                        if sensor_id in state.TOWEL:
                            percent = distance_to_percent(dist)
                            state.TOWEL[sensor_id]["count"] = percent
                            state.TOWEL[sensor_id]["max"] = 100
                            state.TOWEL[sensor_id]["percent"] = percent
                            state.TOWEL[sensor_id]["distance_cm"] = round(dist, 1)
                else:
                    # 신호가 없으면 무한 대기하지 않고 실패로 넘김
                    print(f"[{name}] 측정 실패 (타임아웃 - 배선/센서 점검 필요)")
                
                time.sleep(0.06) 
                
            print("-" * 30)
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("측정 종료")
    except Exception as e:
        print(f"초음파 센서 에러: {e}")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    run()
