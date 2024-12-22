import time
import requests

# Lokasi PWM di sysfs
pwm_chip = "/sys/class/pwm/pwmchip0"
pwm_export = pwm_chip + "/export"
pwm_unexport = pwm_chip + "/unexport"
pwm_period = pwm_chip + "/pwm1/period"
pwm_duty_cycle = pwm_chip + "/pwm1/duty_cycle"
pwm_enable = pwm_chip + "/pwm1/enable"

# URL API untuk mengirim feedback kecepatan
api_url = "http://192.168.114.137:9000/v1/control/"  # Ganti dengan URL API yang benar

# Fungsi untuk menginisialisasi PWM
def init_pwm():
    # Ekspor PWM jika belum diekspor
    try:
        with open(pwm_export, 'w') as f:
            f.write("1")
    except FileExistsError:
        pass
    
    # Set period (contoh: 20ms untuk ESC)
    with open(pwm_period, 'w') as f:
        f.write("20000000")  # 20 ms

    # Aktifkan PWM
    with open(pwm_enable, 'w') as f:
        f.write("1")

# Fungsi untuk mengatur kecepatan motor
def set_motor_speed(speed):
    # Validasi input kecepatan (0-100%)
    if speed < 0 or speed > 100:
        raise ValueError("Kecepatan harus antara 0 dan 100 persen")
    
    # Kalibrasi rentang duty cycle
    min_duty_cycle = 1200000  # 1.2ms (untuk kecepatan 0%)
    max_duty_cycle = 2000000  # 2ms (untuk kecepatan 100%)

    # Hitung duty cycle berdasarkan kecepatan (%)
    duty_cycle = min_duty_cycle + (speed / 100.0) * (max_duty_cycle - min_duty_cycle)
    print(f"Setting duty cycle: {duty_cycle} ns for speed {speed}%")
    with open(pwm_duty_cycle, 'w') as f:
        f.write(str(int(duty_cycle)))

    # Kirim feedback kecepatan ke API
    send_speed_feedback(speed)

# Fungsi untuk mengirim feedback kecepatan ke API
def send_speed_feedback(speed):
    # Format query parameter untuk GET request
    params = {'speed': speed}
    
    try:
        # Mengirim request GET ke API dengan parameter query
        response = requests.get(api_url, params=params)
        
        # Mengecek status respons
        if response.status_code == 200:
            print(f"Kecepatan {speed}% berhasil dikirim ke API")
        else:
            print(f"Error mengirim kecepatan ke API: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Gagal mengirim data ke API: {e}")

# Fungsi untuk menonaktifkan PWM
def disable_pwm():
    with open(pwm_enable, 'w') as f:
        f.write("0")
    with open(pwm_unexport, 'w') as f:
        f.write("1")

if __name__ == "__main__":
    try:
        init_pwm()
        while True:
            # Input kecepatan dari pengguna (0-100%)
            speed = float(input("Masukkan kecepatan motor (0-100%): "))
            set_motor_speed(speed)
            time.sleep(1)  # Beri waktu untuk motor merespon

    except KeyboardInterrupt:
        print("Program dihentikan")
    except ValueError as e:
        print(e)
    finally:
        disable_pwm()
