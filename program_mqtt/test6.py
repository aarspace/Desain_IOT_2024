import smbus
import time
import math

# Alamat I2C untuk MPU-9250
MPU_ADDRESS = 0x68

# Register pada MPU-9250
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
MAG_XOUT_H = 0x03
MAG_XOUT_L = 0x04
MAG_YOUT_H = 0x05
MAG_YOUT_L = 0x06
MAG_ZOUT_H = 0x07
MAG_ZOUT_L = 0x08

# Inisialisasi I2C bus
bus = smbus.SMBus(4)  # Gunakan bus 1 pada Raspberry Pi/Orange Pi

# Variabel global untuk kecepatan (m/s)
velocity_x = 0
velocity_y = 0
velocity_z = 0
previous_time = time.time()

# Fungsi membaca dua byte
def read_word(reg):
    high = bus.read_byte_data(MPU_ADDRESS, reg)
    low = bus.read_byte_data(MPU_ADDRESS, reg + 1)
    value = (high << 8) + low
    return value

def read_word_2c(reg):
    val = read_word(reg)
    if val >= 0x8000:
        return val - 0x10000
    else:
        return val

def init_mpu():
    bus.write_byte_data(MPU_ADDRESS, PWR_MGMT_1, 0)

def read_accel_gyro():
    accel_x = read_word_2c(ACCEL_XOUT_H)
    accel_y = read_word_2c(ACCEL_YOUT_H)
    accel_z = read_word_2c(ACCEL_ZOUT_H)

    gyro_x = read_word_2c(GYRO_XOUT_H)
    gyro_y = read_word_2c(GYRO_YOUT_H)
    gyro_z = read_word_2c(GYRO_ZOUT_H)

    return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z

def read_magnetometer():
    mag_x = read_word(MAG_XOUT_H)
    mag_y = read_word(MAG_YOUT_H)
    mag_z = read_word(MAG_ZOUT_H)
    return mag_x, mag_y, mag_z

def calculate_pitch_roll(accel_x, accel_y, accel_z):
    # Menghitung pitch dan roll dari akselerometer
    pitch = math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2)) * 180 / math.pi
    roll = math.atan2(-accel_x, accel_z) * 180 / math.pi
    return pitch, roll

def calculate_heading(mag_x, mag_y):
    # Menghitung heading (arah mata angin) dari magnetometer
    heading = math.atan2(mag_y, mag_x) * 180 / math.pi
    if heading < 0:
        heading += 360
    return heading

def calculate_velocity(accel_x, accel_y, accel_z):
    global velocity_x, velocity_y, velocity_z, previous_time

    # Menghitung waktu delta
    current_time = time.time()
    delta_time = current_time - previous_time
    previous_time = current_time

    # Faktor konversi untuk akselerasi ke kecepatan
    accel_scale = 16384.0  # sesuai dengan konfigurasi sensor (±2g)

    # Integrasi akselerasi untuk mendapatkan kecepatan
    velocity_x += (accel_x / accel_scale) * delta_time
    velocity_y += (accel_y / accel_scale) * delta_time
    velocity_z += (accel_z / accel_scale) * delta_time

    return velocity_x, velocity_y, velocity_z

def main():
    init_mpu()

    while True:
        accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = read_accel_gyro()
        mag_x, mag_y, mag_z = read_magnetometer()

        # Hitung pitch, roll
        pitch, roll = calculate_pitch_roll(accel_x, accel_y, accel_z)
        print(f"Pitch: {pitch:.2f}°, Roll: {roll:.2f}°")

        # Hitung heading (arah mata angin)
        heading = calculate_heading(mag_x, mag_y)
        print(f"Arah Mata Angin: {heading:.2f}°")

        # Hitung kecepatan
        velocity_x, velocity_y, velocity_z = calculate_velocity(accel_x, accel_y, accel_z)
        print(f"Kecepatan (m/s) - X: {velocity_x:.2f}, Y: {velocity_y:.2f}, Z: {velocity_z:.2f}")

        time.sleep(1)

if __name__ == "__main__":
    main()
