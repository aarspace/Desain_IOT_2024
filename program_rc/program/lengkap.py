import asyncio
import cv2
import websockets
import requests

# Lokasi PWM di sysfs untuk servo PWM2
pwm_chip = "/sys/class/pwm/pwmchip0"
pwm_export = pwm_chip + "/export"
pwm_unexport = pwm_chip + "/unexport"
pwm_period = pwm_chip + "/pwm2/period"
pwm_duty_cycle = pwm_chip + "/pwm2/duty_cycle"
pwm_enable = pwm_chip + "/pwm2/enable"

# Lokasi PWM untuk motor DC brushless di PWM1
dc_pwm_chip = "/sys/class/pwm/pwmchip0"  # Masih di pwmchip0, tetapi menggunakan pwm1
dc_pwm_export = dc_pwm_chip + "/export"
dc_pwm_unexport = dc_pwm_chip + "/unexport"
dc_pwm_period = dc_pwm_chip + "/pwm1/period"  # Menggunakan pwm1
dc_pwm_duty_cycle = dc_pwm_chip + "/pwm1/duty_cycle"
dc_pwm_enable = dc_pwm_chip + "/pwm1/enable"

# URL API untuk mendapatkan data sudut dan kecepatan dari REST API
api_url = "http://172.188.64.30:9000/v1/control"  # Ganti dengan URL API yang benar

# Fungsi untuk melepaskan PWM
def unexport_pwm():
    try:
        with open(pwm_unexport, 'w') as f:
            f.write("2")  # Unexport PWM2
    except Exception as e:
        print(f"Error unexporting PWM: {e}")

# Fungsi untuk melepaskan PWM motor DC
def unexport_dc_motor_pwm():
    try:
        with open(dc_pwm_unexport, 'w') as f:
            f.write("1")  # Unexport PWM1
    except Exception as e:
        print(f"Error unexporting DC motor PWM: {e}")

# Fungsi untuk menginisialisasi PWM
def init_pwm():
    # Lepaskan PWM2 sebelum diekspor
    unexport_pwm()
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
    # Konversi degree menjadi float
    degree = float(degree)
    
    # Validasi input sudut (0-90 derajat)
    if degree < 0 or degree > 90:
        raise ValueError("Sudut harus antara 0 dan 90 derajat")
    
    # Kalibrasi rentang duty cycle
    min_duty_cycle = 1200000  # 1.2ms (untuk sudut 0)
    max_duty_cycle = 2000000  # 2ms (untuk sudut 90)

    # Hitung duty cycle berdasarkan sudut (degree)
    duty_cycle = min_duty_cycle + (degree / 90.0) * (max_duty_cycle - min_duty_cycle)
    print(f"Setting servo duty cycle: {duty_cycle} ns for degree {degree} degrees")
    with open(pwm_duty_cycle, 'w') as f:
        f.write(str(int(duty_cycle)))

# Fungsi untuk menginisialisasi motor DC
def init_dc_motor():
    # Lepaskan motor DC sebelum diekspor
    unexport_dc_motor_pwm()
    try:
        with open(dc_pwm_export, 'w') as f:
            f.write("1")  # Ekspor PWM untuk motor DC (PWM1)
    except FileExistsError:
        pass
    
    # Set period untuk motor DC
    with open(dc_pwm_period, 'w') as f:
        f.write("20000000")  # 20 ms

    # Aktifkan PWM untuk motor DC
    with open(dc_pwm_enable, 'w') as f:
        f.write("1")

# Fungsi untuk mengatur kecepatan motor DC brushless
def set_dc_motor_speed(speed):
    # Konversi speed menjadi float
    speed = float(speed)

    # Validasi input kecepatan (0-100%)
    if speed < 0 or speed > 100:
        raise ValueError("Kecepatan harus antara 0 dan 100%")
    
    # Menghitung duty cycle berdasarkan kecepatan (0-100%)
    min_duty_cycle = 1200000  # 1.2ms (untuk kecepatan 0%)
    max_duty_cycle = 2000000  # 2ms (untuk kecepatan 100%)
    
    duty_cycle = min_duty_cycle + (speed / 100.0) * (max_duty_cycle - min_duty_cycle)
    print(f"Setting DC motor duty cycle: {duty_cycle} ns for speed {speed}%")
    with open(dc_pwm_duty_cycle, 'w') as f:
        f.write(str(int(duty_cycle)))

# Fungsi untuk mendapatkan sudut dan kecepatan dari API
def get_parameters_from_api():
    try:
        # Mengirim permintaan GET ke URL API
        response = requests.get(api_url)
        
        # Memeriksa apakah respons berhasil (status code 200)
        if response.status_code == 200:
            # Menguraikan data JSON dari respons
            data = response.json()
            
            # Mendapatkan nilai sudut dan kecepatan dari data JSON
            degree = data.get("degree")
            speed = data.get("speed")
            return degree, speed
        else:
            print(f"Gagal mendapatkan data dari API. Status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan saat mencoba mengakses API: {e}")

    return None, None

async def send_images():
    # Koneksi ke WebSocket server
    async with websockets.connect("ws://172.188.64.30:9999/sender") as websocket:
        # Membuka kamera (0 biasanya untuk kamera internal atau webcam USB pertama)
        cap = cv2.VideoCapture(1)

        # Cek apakah kamera berhasil dibuka
        if not cap.isOpened():
            print("Kamera tidak terdeteksi! Pastikan kamera USB terhubung.")
            return  # Keluar dari fungsi jika kamera tidak terdeteksi
        
        # Inisialisasi PWM untuk servo dan motor DC
        init_pwm()
        init_dc_motor()

        try:
            while True:
                # Mendapatkan sudut dan kecepatan dari API
                degree, speed = get_parameters_from_api()
                if degree is not None:
                    set_servo_degree(degree)
                if speed is not None:
                    set_dc_motor_speed(speed)

                # Membaca frame dari kamera
                ret, frame = cap.read()
                if not ret:
                    print("Tidak dapat membaca frame dari kamera!")
                    break

                # Encode frame sebagai JPEG
                buffer = cv2.imencode('.jpg', frame)[1].tobytes()

                # Mengirimkan data gambar (JPEG) ke server WebSocket
                await websocket.send(buffer)

                # Tunggu sedikit sebelum mengirim frame berikutnya (untuk mengontrol frame rate)
                await asyncio.sleep(0.05)  # Mengirim frame dengan interval sekitar 20 fps

        finally:
            # Pastikan kamera dilepas setelah streaming selesai
            cap.release()
            print("Kamera dilepas.")
            # Nonaktifkan PWM setelah selesai
            unexport_pwm()
            unexport_dc_motor_pwm()

# Jalankan fungsi send_images dengan asyncio event loop
if __name__ == "__main__":
    asyncio.run(send_images())
