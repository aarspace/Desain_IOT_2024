import smbus
import time

def scan_i2c_bus():
    # Inisialisasi I2C bus (I2C bus 1 pada Orange Pi Zero)
    bus = smbus.SMBus(1)
    
    # Pemindaian untuk alamat I2C dari 0x03 hingga 0x77 (0x00 hingga 0x02 adalah alamat yang dikhususkan dan biasanya tidak digunakan)
    print("Scanning I2C addresses...")
    for address in range(3, 128):  # Alamat I2C umumnya dari 0x03 hingga 0x77
        try:
            # Coba untuk membaca satu byte dari alamat ini
            bus.read_byte(address)
            print(f"Found device at address 0x{address:02X}")
        except Exception as e:
            # Jika gagal membaca, maka alamat ini tidak ada perangkat yang terhubung
            pass

if __name__ == "__main__":
    scan_i2c_bus()
