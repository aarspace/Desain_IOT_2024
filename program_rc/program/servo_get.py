import time
import requests

# Lokasi PWM di sysfs untuk PWM2
pwm_chip = "/sys/class/pwm/pwmchip0"
pwm_export = pwm_chip + "/export"
pwm_unexport = pwm_chip + "/unexport"
pwm_period = pwm_chip + "/pwm2/period"        # Mengubah dari pwm1 ke pwm2
pwm_duty_cycle = pwm_chip + "/pwm2/duty_cycle" # Mengubah dari pwm1 ke pwm2
pwm_enable = pwm_chip + "/pwm2/enable"        # Mengubah dari pwm1 ke pwm2

# URL API untuk mendapatkan data sudut dari REST API
api_url = "http://172.188.64.30:9000/v1/control"  # Ganti dengan URL API yang benar

# Fungsi untuk menginisialisasi PWM
def init_pwm():
    # Ekspor PWM2 jika belum diekspor
    try:
        with open(pwm_export, 'w') as f:
            f.write("2")  # Ekspor PWM2
    except FileExistsError:
        pass
    
    # Set period (contoh: 20ms untuk servo)
    with open(pwm_period, 'w') as f:
        f.write("20000000")  # 20 ms

    # Aktifkan PWM2
    with open(pwm_enable, 'w') as f:
        f.write("1")

# Fungsi untuk mengatur sudut servo (dalam derajat)
def set_servo_degree(degree):
    # Validasi input sudut (0-90 derajat)
    if degree < 0 or degree > 90:
        raise ValueError("Sudut harus antara 0 dan 90 derajat")
    
    # Kalibrasi rentang duty cycle
    min_duty_cycle = 1200000  # 1.2ms (untuk sudut 0)
    max_duty_cycle = 2000000  # 2ms (untuk sudut 90)

    # Hitung duty cycle berdasarkan sudut (degree)
    duty_cycle = min_duty_cycle + (degree / 90.0) * (max_duty_cycle - min_duty_cycle)
    print(f"Setting duty cycle: {duty_cycle} ns for degree {degree} degrees")
    with open(pwm_duty_cycle, 'w') as f:
        f.write(str(int(duty_cycle)))

# Fungsi untuk mengirim feedback sudut ke API (opsional, jika diperlukan)
def send_degree_feedback(degree):
    # Format query parameter untuk GET request
    params = {'degree': degree}
    
    try:
        # Mengirim request GET ke API dengan parameter query
        response = requests.get(api_url, params=params)
        
        # Mengecek status respons
        if response.status_code == 200:
            print(f"Sudut {degree} derajat berhasil dikirim ke API")
        else:
            print(f"Error mengirim sudut ke API: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Gagal mengirim data ke API: {e}")

# Fungsi untuk mendapatkan sudut dari API
def get_degree_from_api():
    try:
        # Mengirim permintaan GET ke URL API
        response = requests.get(api_url)
        
        # Memeriksa apakah respons berhasil (status code 200)
        if response.status_code == 200:
            # Menguraikan data JSON dari respons
            data = response.json()
            
            # Mendapatkan nilai sudut dari data JSON
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

# Fungsi untuk menonaktifkan PWM
def disable_pwm():
    with open(pwm_enable, 'w') as f:
        f.write("0")
    with open(pwm_unexport, 'w') as f:
        f.write("2")

if __name__ == "__main__":
    try:
        init_pwm()
        while True:
            # Mendapatkan sudut dari API
            degree = get_degree_from_api()
            if degree is not None:
                set_servo_degree(degree)
            
            # Tunggu selama 1 detik sebelum cek lagi
            time.sleep(1)

    except KeyboardInterrupt:
        print("Program dihentikan")
    except ValueError as e:
        print(e)
    finally:
        disable_pwm()
