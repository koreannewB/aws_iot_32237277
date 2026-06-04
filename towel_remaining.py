import RPi.GPIO as GPIO
import time
import state

ULTRASONIC_SENSORS = {
    "sensor_1": {"trig": 23, "echo": 24},
    "sensor_2": {"trig": 25, "echo": 8},
    "sensor_3": {"trig": 9,  "echo": 11},
}

EMPTY_DIST = 15.0  # distance when no towels (cm)
FULL_DIST  =  3.0  # distance when full (cm)

def dist_to_count(dist, max_count):
    dist = max(FULL_DIST, min(EMPTY_DIST, dist))
    ratio = (EMPTY_DIST - dist) / (EMPTY_DIST - FULL_DIST)
    return round(ratio * max_count)

def setup_ultrasonic():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for name, pins in ULTRASONIC_SENSORS.items():
        GPIO.setup(pins["trig"], GPIO.OUT)
        GPIO.setup(pins["echo"], GPIO.IN)
        GPIO.output(pins["trig"], False)
    print("[Towel] Ultrasonic sensors initialized, stabilizing...")
    time.sleep(2)

def measure_distance(trig, echo):
    # stabilize before pulse (noise prevention)
    GPIO.output(trig, False)
    time.sleep(0.002)

    # send 10us pulse
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
                sensor_id = int(name.split("_")[1])

                if dist is not None:
                    if dist > 400:
                        print(f"[Towel] #{sensor_id} abnormal value: {dist:.2f}cm (ignored)")
                    else:
                        if sensor_id in state.TOWEL:
                            max_count = state.TOWEL[sensor_id]["max"]
                            count = dist_to_count(dist, max_count)
                            state.TOWEL[sensor_id]["count"] = count
                            print(f"[Towel] #{sensor_id} {dist:.1f}cm → {count}/{max_count}")
                else:
                    print(f"[Towel] #{sensor_id} timeout")

                # wait for echo to clear between sensors
                time.sleep(0.06)

            # wait after full cycle
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("[Towel] Stopped")
    except Exception as e:
        print(f"[Towel] Error: {e}")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    run()