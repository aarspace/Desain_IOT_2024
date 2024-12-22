import time
import requests
import asyncio
import cv2
import websockets

# Lokasi PWM di sysfs
pwm_chip = "/sys/class/pwm/pwmchip0"
pwm_export = pwm_chip + "/export"
pwm_unexport = pwm_chip + "/unexport"
pwm_period = pwm_chip + "/pwm1/period"
pwm_duty_cycle = pwm_chip + "/pwm1/duty_cycle"
pwm_enable = pwm_chip + "/pwm1/enable"

# URL API untuk mengirim dan menerima kecepatan
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

    # Kirim feedback kecepatan ke API menggunakan GET
    send_speed_feedback(speed)

# Fungsi untuk mengirim feedback kecepatan ke API menggunakan GET
def send_speed_feedback(speed):
    params = {'speed': speed}
    try:
        response = requests.get(api_url, params=params)
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

# Fungsi untuk mendapatkan kecepatan dari API
def get_speed_from_api():
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            speed = data.get("speed")
            if speed is not None:
                return float(speed)
            else:
                print("Data speed tidak ditemukan dalam respons")
        else:
            print(f"Gagal mendapatkan data dari API. Status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan saat mencoba mengakses API: {e}")

    return None

# Fungsi untuk mengirimkan gambar melalui WebSocket
async def send_images():
    async with websockets.connect("ws://192.168.114.137:9999/sender") as websocket:
        cap = cv2.VideoCapture(1)

        if not cap.isOpened():
            print("Kamera tidak terdeteksi! Pastikan kamera USB terhubung.")
            return

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Tidak dapat membaca frame dari kamera!")
                    break

                buffer = cv2.imencode('.jpg', frame)[1].tobytes()
                await websocket.send(buffer)
                await asyncio.sleep(0.05)  # Sekitar 20 fps
        finally:
            cap.release()
            print("Kamera dilepas.")

# Fungsi utama untuk menjalankan kontrol PWM
async def pwm_control_loop():
    try:
        init_pwm()
        while True:
            speed = get_speed_from_api()
            if speed is not None:
                set_motor_speed(speed)
            await asyncio.sleep(1)  # Tunggu 1 detik sebelum cek lagi
    except KeyboardInterrupt:
        print("Program PWM dihentikan")
    except ValueError as e:
        print(e)
    finally:
        disable_pwm()

# Fungsi untuk menjalankan kedua tugas secara bersamaan
async def main():
    await asyncio.gather(
        send_images(),
        pwm_control_loop()
    )

# Jalankan event loop asyncio untuk kedua tugas
asyncio.get_event_loop().run_until_complete(main())
