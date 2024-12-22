import smbus
import time

# Alamat I2C untuk MPU-6050 atau MPU-9250 (biasanya 0x68)
MPU_ADDRESS = 0x68

# Register pada MPU-6050
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
ACCEL_XOUT_L = 0x3C
ACCEL_YOUT_H = 0x3D
ACCEL_YOUT_L = 0x3E
ACCEL_ZOUT_H = 0x3F
ACCEL_ZOUT_L = 0x40
GYRO_XOUT_H = 0x43
GYRO_XOUT_L = 0x44
GYRO_YOUT_H = 0x45
GYRO_YOUT_L = 0x46
GYRO_ZOUT_H = 0x47
GYRO_ZOUT_L = 0x48

# Inisialisasi I2C bus
bus = smbus.SMBus(4)  # Gunakan bus 1 pada Raspberry Pi/Orange Pi

def read_word(reg):
    # Membaca 2 byte dari register
    high = bus.read_byte_data(MPU_ADDRESS, reg)
    low = bus.read_byte_data(MPU_ADDRESS, reg + 1)
    value = (high << 8) + low
    return value

def read_word_2c(reg):
    # Membaca data dan konversi ke signed integer
    val = read_word(reg)
    if val >= 0x8000:
        return val - 0x10000
    else:
        return val

def init_mpu():
    # Menghentikan sleep mode (mengaktifkan sensor)
    bus.write_byte_data(MPU_ADDRESS, PWR_MGMT_1, 0)

def read_accel_gyro():
    # Membaca nilai akselerometer dan gyroscope
    accel_x = read_word_2c(ACCEL_XOUT_H)
    accel_y = read_word_2c(ACCEL_YOUT_H)
    accel_z = read_word_2c(ACCEL_ZOUT_H)

    gyro_x = read_word_2c(GYRO_XOUT_H)
    gyro_y = read_word_2c(GYRO_YOUT_H)
    gyro_z = read_word_2c(GYRO_ZOUT_H)

    return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z

def main():
    init_mpu()

    while True:
        accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = read_accel_gyro()
        print(f"Accelerometer (X, Y, Z): {accel_x}, {accel_y}, {accel_z}")
        print(f"Gyroscope (X, Y, Z): {gyro_x}, {gyro_y}, {gyro_z}")
        time.sleep(1)

if __name__ == "__main__":
    main()
