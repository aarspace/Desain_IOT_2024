import time
import smbus
import math

# I2C address of MPU9250
MPU9250_ADDR = 0x68  # Address of MPU9250
MAG_ADDR = 0x0C  # Address of Magnetometer (AK8963)

# Initialize I2C (SMBus)
bus = smbus.SMBus(4)  # Use I2C bus 1 on Orange Pi Zero

def read_byte(addr, reg):
    """ Read one byte from the given register """
    return bus.read_byte_data(addr, reg)

def read_word(addr, reg):
    """ Read two bytes from the given register and return as a 16-bit word """
    high = bus.read_byte_data(addr, reg)
    low = bus.read_byte_data(addr, reg + 1)
    val = (high << 8) + low
    if val >= 0x8000:
        return val - 0x10000  # Handle signed 16-bit value
    else:
        return val

def read_word_2c(addr, reg):
    """ Read a signed 16-bit word from the given register """
    val = read_word(addr, reg)
    if val >= 0x8000:
        return val - 0x10000
    else:
        return val

def initialize_mpu9250():
    """ Initialize MPU9250 by writing to the MPU9250 registers """
    bus.write_byte_data(MPU9250_ADDR, 0x6B, 0)  # Wake up MPU9250
    bus.write_byte_data(MPU9250_ADDR, 0x1B, 0x00)  # Gyroscope full-scale range: ±250 degrees/s
    bus.write_byte_data(MPU9250_ADDR, 0x1C, 0x00)  # Accelerometer full-scale range: ±2g

def initialize_magnetometer():
    """ Initialize Magnetometer (AK8963) """
    bus.write_byte_data(MAG_ADDR, 0x0A, 0x01)  # Continuous measurement mode

def read_accel_data():
    """ Read accelerometer data (X, Y, Z) """
    ax = read_word_2c(MPU9250_ADDR, 0x3B) / 16384.0  # Divide by sensitivity scale factor (16384 for ±2g)
    ay = read_word_2c(MPU9250_ADDR, 0x3D) / 16384.0
    az = read_word_2c(MPU9250_ADDR, 0x3F) / 16384.0
    return ax, ay, az

def read_gyro_data():
    """ Read gyroscope data (X, Y, Z) """
    gx = read_word_2c(MPU9250_ADDR, 0x43) / 131.0  # Divide by sensitivity scale factor (131 for ±250 degrees/s)
    gy = read_word_2c(MPU9250_ADDR, 0x45) / 131.0
    gz = read_word_2c(MPU9250_ADDR, 0x47) / 131.0
    return gx, gy, gz

def read_mag_data():
    """ Read magnetometer data (X, Y, Z) """
    mx = read_word_2c(MAG_ADDR, 0x03)
    my = read_word_2c(MAG_ADDR, 0x05)
    mz = read_word_2c(MAG_ADDR, 0x07)
    return mx, my, mz

def calculate_inclination(ax, ay, az):
    """ Calculate pitch and roll angles (in degrees) from accelerometer data """
    pitch = math.atan2(ay, math.sqrt(ax**2 + az**2)) * 180.0 / math.pi
    roll = math.atan2(-ax, az) * 180.0 / math.pi
    return pitch, roll

def calculate_heading(mx, my):
    """ Calculate heading (compass) from magnetometer data """
    heading = math.atan2(my, mx) * 180.0 / math.pi
    if heading < 0:
        heading += 360
    return heading

def main():
    """ Main function to run the sensor readings and calculations """
    initialize_mpu9250()
    initialize_magnetometer()

    while True:
        # Read accelerometer and gyroscope data
        ax, ay, az = read_accel_data()
        gx, gy, gz = read_gyro_data()

        # Read magnetometer data
        mx, my, mz = read_mag_data()

        # Calculate pitch, roll, and heading (compass)
        pitch, roll = calculate_inclination(ax, ay, az)
        heading = calculate_heading(mx, my)

        # Print out the results
        print(f"Accelerometer: ax={ax:.2f}g, ay={ay:.2f}g, az={az:.2f}g")
        print(f"Gyroscope: gx={gx:.2f}°/s, gy={gy:.2f}°/s, gz={gz:.2f}°/s")
        print(f"Pitch={pitch:.2f}° Roll={roll:.2f}° Heading={heading:.2f}°")
        print("------------------------------------------------")
        time.sleep(1)

if __name__ == "__main__":
    main()
