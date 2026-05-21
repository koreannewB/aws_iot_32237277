import smbus2
import time
import math

# MPU-6050 레지스터 주소
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B

# 사진에 명시된 I2C 주소 (AD0 핀 상태에 따라 다름)
MPU_ADDRS = {
    "sensor_1": 0x68,  # AD0 -> GND
    "sensor_2": 0x69   # AD0 -> 3.3V
}

bus = smbus2.SMBus(1)  # I2C 버스 1 사용

def init_mpu6050(addr):
    try:
        # 슬립 모드 해제 (0을 기록하여 센서 깨우기)
        bus.write_byte_data(addr, PWR_MGMT_1, 0)
        return True
    except Exception as e:
        print(f"I2C 주소 {hex(addr)} 초기화 실패: {e}")
        return False

def read_raw_data(addr, reg):
    # 상위 8비트, 하위 8비트를 읽어서 합침
    high = bus.read_byte_data(addr, reg)
    low = bus.read_byte_data(addr, reg+1)
    value = ((high << 8) | low)
    # 부호 있는 16비트 정수로 변환
    if value > 32768:
        value = value - 65536
    return value

def get_accel_data(addr):
    try:
        acc_x = read_raw_data(addr, ACCEL_XOUT_H)
        acc_y = read_raw_data(addr, ACCEL_XOUT_H + 2)
        acc_z = read_raw_data(addr, ACCEL_XOUT_H + 4)
        
        # MPU-6050 기본 세팅(±2g)에서 1g = 16384 LSB
        Ax = acc_x / 16384.0
        Ay = acc_y / 16384.0
        Az = acc_z / 16384.0
        
        return Ax, Ay, Az
    except Exception as e:
        return None, None, None

def calculate_magnitude(ax, ay, az):
    return math.sqrt(ax**2 + ay**2 + az**2)

if __name__ == '__main__':
    # 센서 초기화
    for name, addr in MPU_ADDRS.items():
        if init_mpu6050(addr):
            print(f"{name} ({hex(addr)}) 초기화 성공")
    
    time.sleep(1)
    
    try:
        while True:
            for name, addr in MPU_ADDRS.items():
                ax, ay, az = get_accel_data(addr)
                if ax is not None:
                    mag = calculate_magnitude(ax, ay, az)
                    print(f"[{name}] Ax: {ax:.2f}g, Ay: {ay:.2f}g, Az: {az:.2f}g | 크기(Mag): {mag:.2f}g")
                else:
                    print(f"[{name}] 데이터 읽기 실패")
            print("-" * 40)
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("측정 종료")