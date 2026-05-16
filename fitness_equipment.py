import time
import state

# MPU-6050 I2C 주소 및 레지스터
MPU6050_ADDR = 0x68
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B

# 가속도 변화량 임계값 (단위: g) - 이 값 이상이면 사용 중으로 판단
MOTION_THRESHOLD = 0.15
# 사용 중 판정 후 유지 시간 (초) - 움직임이 없어도 이 시간 동안은 in_use 유지
COOLDOWN_SEC = 5.0
MEASURE_INTERVAL = 0.2

# 장비 id → I2C 멀티플렉서 채널 (TCA9548A) 또는 단순 주소 매핑
# 실제 배선에 맞게 수정하세요
EQUIPMENT_CHANNELS = {
    1: 0,  # 벤치프레스  → ch0
    2: 1,  # 덤벨 랙    → ch1
    3: 2,  # 스쿼트 랙  → ch2
    4: 3,  # 레그프레스 → ch3
    5: 4,  # 케이블 머신→ ch4
    6: 5,  # 풀업 바    → ch5
}

TCA9548A_ADDR = 0x70


def _select_channel(bus, ch):
    """TCA9548A 멀티플렉서 채널 선택"""
    bus.write_byte(TCA9548A_ADDR, 1 << ch)


def _read_accel(bus):
    """MPU-6050에서 가속도 3축 읽기 → (ax, ay, az) in g"""
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)  # wake up
    raw = bus.read_i2c_block_data(MPU6050_ADDR, ACCEL_XOUT_H, 6)
    def to_signed(h, l):
        val = (h << 8) | l
        return val - 65536 if val > 32767 else val
    ax = to_signed(raw[0], raw[1]) / 16384.0
    ay = to_signed(raw[2], raw[3]) / 16384.0
    az = to_signed(raw[4], raw[5]) / 16384.0
    return ax, ay, az


def _magnitude(ax, ay, az):
    return (ax**2 + ay**2 + az**2) ** 0.5


def run():
    try:
        import smbus2
        bus = smbus2.SMBus(1)
        print("[equipment] I2C 초기화 완료")

        # 각 장비별 직전 가속도 크기 및 마지막 움직임 시각 추적
        prev_mag  = {eq_id: None for eq_id in EQUIPMENT_CHANNELS}
        last_move = {eq_id: 0.0  for eq_id in EQUIPMENT_CHANNELS}

        while True:
            for eq in state.EQUIPMENT:
                eq_id = eq["id"]
                if eq_id not in EQUIPMENT_CHANNELS:
                    continue
                ch = EQUIPMENT_CHANNELS[eq_id]
                try:
                    _select_channel(bus, ch)
                    ax, ay, az = _read_accel(bus)
                    mag = _magnitude(ax, ay, az)

                    if prev_mag[eq_id] is not None:
                        delta = abs(mag - prev_mag[eq_id])
                        if delta >= MOTION_THRESHOLD:
                            last_move[eq_id] = time.time()

                    prev_mag[eq_id] = mag

                    in_use = (time.time() - last_move[eq_id]) < COOLDOWN_SEC
                    eq["in_use"] = 1 if in_use else 0
                    eq["status"] = "in_use" if in_use else "available"

                except Exception as e:
                    print(f"[equipment] {eq_id}번({eq['name']}) 읽기 오류: {e}")

            time.sleep(MEASURE_INTERVAL)

    except ImportError:
        print("[equipment] smbus2 없음 - 더미 모드 실행 (PC 테스트용)")
        _run_dummy()


def _run_dummy():
    import math
    t = 0.0
    while True:
        for eq in state.EQUIPMENT:
            # 장비마다 다른 주기로 in_use 0↔1 토글
            period = 6 + eq["id"] * 2
            in_use = 1 if math.sin(t * (2 * math.pi / period)) > 0 else 0
            eq["in_use"] = in_use
            eq["status"] = "in_use" if in_use else "available"
        t += MEASURE_INTERVAL
        time.sleep(MEASURE_INTERVAL)
