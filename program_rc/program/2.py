import time
import requests

# Lokasi PWM di sysfs untuk PWM1 dan PWM2
pwm_chip = "/sys/class/pwm/pwmchip0"
pwm_export = pwm_chip + "/export"
pwm_unexport = pwm_chip + "/unexport"

# PWM untuk Servo (PWM2)
pwm2_period = pwm_chip + "/pwm2/period"
pwm2_duty_cycle = pwm_chip + "/pwm2/duty_cycle"
pwm2_enable = pwm_chip + "/pwm2/enable"

# PWM untuk Motor (PWM1)
pwm1_period = pwm_chip + "/pwm1/period"
pwm1_duty_cycle = pwm_chip + "/pwm1/duty_cycle"
pwm1_enable = pwm_chip + "/pwm1/enable"

# URL API untuk mendapatkan data sudut servo dan mengirim feedback kecepatan
api_url_degree = "http://192.168.114.137:9000/v1/control"
api_url_speed = "http://192.168.114.137:9000/v1/control/"

# Fungsi untuk menginisialisasi PWM
def init_pwm():
    # Ekspor PWM1 dan PWM2 jika belum diekspor
    try:
        with open(pwm_export, 'w') as f:
            f.write("1")  # Ekspor PWM1 untuk motor
            f.write("2")  # Ekspor PWM2 untuk servo
    except FileExistsError:
        pass
    
    # Set period (contoh: 20ms untuk motor dan servo)
    with open(pwm1_period, 'w') as f:
        f.write("20000000")  # 20 ms untuk motor
    with open(pwm2_period, 'w') as f:
        f.write("20000000")  # 20 ms untuk servo

    # Aktifkan PWM1 (motor) dan PWM2 (servo)
    with open(pwm1_enable, 'w') as f:
        f.write("1")
    with open(pwm2_enable, 'w') as f:
        f.write("1")

# Fungsi untuk mengatur sudut servo (PWM2)
def set_servo_degree(degree):
    # Validasi input sudut (0-90 derajat)
    if degree < 0 or degree > 90:
        raise ValueError("Sudut harus antara 0 dan 90 derajat")
    
    # Kalibrasi rentang duty cycle
    min_duty_cycle = 1200000  # 1.2ms (untuk sudut 0)
    max_duty_cycle = 2000000  # 2ms (untuk sudut 90)

    # Hitung duty cycle berdasarkan sudut
    duty_cycle = min_duty_cycle + (degree / 90.0) * (max_duty_cycle - min_duty_cycle)
    print(f"Setting duty cycle: {duty_cycle} ns for degree {degree} degrees")
    with open(pwm2_duty_cycle, 'w') as f:
        f.write(str(int(duty_cycle)))

# Fungsi untuk mendapatkan sudut dari API
def get_degree_from_api():
    try:
        response = requests.get(api_url_degree)
        if response.status_code == 200:
            data = response.json()
            degree = data.get("degree")
            if degree is not None:
                return float(degree)
            else:
                print("Data sudut tidak ditemukan dalam respons")
        else:
            print(f"Gagal mendapatkan data dari API. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan saat mencoba mengakses API: {e}")

    return None

# Fungsi untuk mengatur kecepatan motor (PWM1)
def set_motor_speed(speed):
    if speed < 0 or speed > 100:
        raise ValueError("Kecepatan harus antara 0 dan 100 persen")
    
    min_duty_cycle = 1200000  # 1.2ms (untuk kecepatan 0%)
    max_duty_cycle = 2000000  # 2ms (untuk kecepatan 100%)

    # Hitung duty cycle berdasarkan kecepatan
    duty_cycle = min_duty_cycle + (speed / 100.0) * (max_duty_cycle - min_duty_cycle)
    print(f"Setting duty cycle: {duty_cycle} ns for speed {speed}%")
    with open(pwm1_duty_cycle, 'w') as f:
        f.write(str(int(duty_cycle)))

    # Kirim feedback kecepatan ke API
    send_speed_feedback(speed)

# Fungsi untuk mengirim feedback kecepatan ke API
def send_speed_feedback(speed):
    params = {'speed': speed}
    try:
        response = requests.get(api_url_speed, params=params)
        if response.status_code == 200:
            print(f"Kecepatan {speed}% berhasil dikirim ke API")
        else:
            print(f"Error mengirim kecepatan ke API: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Gagal mengirim data ke API: {e}")

# Fungsi untuk menonaktifkan PWM
def disable_pwm():
    with open(pwm1_enable, 'w') as f:
        f.write("0")
    with open(pwm2_enable, 'w') as f:
        f.write("0")
    with open(pwm_unexport, 'w') as f:
        f.write("1")
        f.write("2")

if __name__ == "__main__":
    try:
        init_pwm()
        while True:
            # Dapatkan sudut dari API dan atur servo
            degree = get_degree_from_api()
            if degree is not None:
                set_servo_degree(degree)
            
            # Minta kecepatan motor dari pengguna dan atur motor
            speed = float(input("Masukkan kecepatan motor (0-100%): "))
            set_motor_speed(speed)

            time.sleep(1)  # Tunggu 1 detik sebelum mengulangi loop

    except KeyboardInterrupt:
        print("Program dihentikan")
    except ValueError as e:
        print(e)
    finally:
        disable_pwm()
