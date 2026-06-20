# import smbus2
# import time
# import math
# import state # 웹서버와 데이터 공유

# PWR_MGMT_1   = 0x6B
# ACCEL_XOUT_H = 0x3B

# MPU_ADDRS = {
#     0: 0x68,  # state.EQUIPMENT의 0번째 인덱스 (벤치프레스)
#     1: 0x69   # state.EQUIPMENT의 1번째 인덱스 (덤벨 랙)
# }

# bus = None

# def init_mpu6050(addr):
#     try:
#         bus.write_byte_data(addr, PWR_MGMT_1, 0)
#         return True
#     except Exception:
#         return False

# def read_raw_data(addr, reg):
#     high = bus.read_byte_data(addr, reg)
#     low = bus.read_byte_data(addr, reg+1)
#     value = ((high << 8) | low)
#     return value - 65536 if value > 32768 else value

# def get_accel_data(addr):
#     try:
#         acc_x = read_raw_data(addr, ACCEL_XOUT_H)
#         acc_y = read_raw_data(addr, ACCEL_XOUT_H + 2)
#         acc_z = read_raw_data(addr, ACCEL_XOUT_H + 4)
#         return acc_x / 16384.0, acc_y / 16384.0, acc_z / 16384.0
#     except Exception:
#         return None, None, None

# def calculate_magnitude(ax, ay, az):
#     return math.sqrt(ax**2 + ay**2 + az**2)

# # main.py의 스레드에서 실행될 run 함수
# def run():
#     global bus
#     try:
#         bus = smbus2.SMBus(1)
#     except Exception as e:
#         print(f"[Equipment] I2C 버스 초기화 실패: {e}")
#         return

#     for idx, addr in MPU_ADDRS.items():
#         init_mpu6050(addr)
#     print("[Equipment] 가속도 센서 감지 스레드 시작")

#     while True:
#         for idx, addr in MPU_ADDRS.items():
#             ax, ay, az = get_accel_data(addr)
#             if ax is not None:
#                 mag = calculate_magnitude(ax, ay, az)

#                 # [로직] 중력가속도(1.0g)를 기준으로 1.2g 이상 흔들림이 발생하면 사용 중으로 간주
#                 # 민감도를 바꾸고 싶다면 1.2 숫자를 조절하세요.
#                 is_in_use = mag > 1.2

#                 # state.py 업데이트 (웹서버로 전송됨)
#                 if idx < len(state.EQUIPMENT):
#                     state.EQUIPMENT[idx]["id"]     = idx + 1          # ← 추가 (JS id와 맞춤)
#                     state.EQUIPMENT[idx]["status"] = "in_use" if is_in_use else "available"
#                     state.EQUIPMENT[idx]["in_use"] = 1 if is_in_use else 0

#         time.sleep(0.5)  # 0.5초마다 측정


import time
import state

def run():
    in_use = False

    while True:
        in_use = not in_use

        state.EQUIPMENT[0]["status"] = \
            "in_use" if in_use else "available"

        state.EQUIPMENT[0]["in_use"] = \
            1 if in_use else 0

        state.EQUIPMENT[1]["status"] = "available"
        state.EQUIPMENT[1]["in_use"] = 0

        time.sleep(5)