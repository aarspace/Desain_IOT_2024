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

def read_accel():
    accel_x = read_word_2c(ACCEL_XOUT_H)
    accel_y = read_word_2c(ACCEL_YOUT_H)
    accel_z = read_word_2c(ACCEL_ZOUT_H)
    return accel_x, accel_y, accel_z

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

def heading_to_direction(heading):
    # Menentukan arah berdasarkan heading (arah mata angin)
    if (heading >= 0 and heading < 45) or (heading >= 315 and heading < 360):
        return "Utara"
    elif heading >= 45 and heading < 135:
        return "Timur"
    elif heading >= 135 and heading < 225:
        return "Selatan"
    elif heading >= 225 and heading < 315:
        return "Barat"

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

    # Menghitung kecepatan total (dalam m/s)
    velocity_total = math.sqrt(velocity_x**2 + velocity_y**2 + velocity_z**2)

    # Batasi kecepatan minimum
    if velocity_total < 0.1:  # Batasi kecepatan yang sangat rendah
        velocity_total = 0.0

    # Mengkonversi kecepatan ke dalam km/h
    velocity_kmh = velocity_total * 3.6

    return velocity_total, velocity_kmh

def main():
    init_mpu()

    while True:
        accel_x, accel_y, accel_z = read_accel()
        mag_x, mag_y, mag_z = read_magnetometer()

        # Hitung pitch, roll
        pitch, roll = calculate_pitch_roll(accel_x, accel_y, accel_z)
        print(f"Kemiringan: {pitch:.2f}° (Pitch), {roll:.2f}° (Roll)")

        # Hitung heading (arah mata angin)
        heading = calculate_heading(mag_x, mag_y)
        direction = heading_to_direction(heading)
        print(f"Arah Mata Angin: {direction} ({heading:.2f}°)")

        # Hitung kecepatan
        velocity_total, velocity_kmh = calculate_velocity(accel_x, accel_y, accel_z)
        if velocity_total < 0.1:
            print("Kecepatan: 0 km/h (Objek berhenti)")
        else:
            print(f"Kecepatan: {velocity_kmh:.2f} km/h ({velocity_total:.2f} m/s)")

        time.sleep(1)

if __name__ == "__main__":
    main()
