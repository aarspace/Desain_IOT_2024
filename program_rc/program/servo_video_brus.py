import time
import requests
import asyncio
import cv2
import websockets

# Lokasi PWM untuk servo (pwm2) di sysfs
pwm_chip_servo = "/sys/class/pwm/pwmchip0"
pwm_export_servo = pwm_chip_servo + "/export"
pwm_unexport_servo = pwm_chip_servo + "/unexport"
pwm_period_servo = pwm_chip_servo + "/pwm2/period"
pwm_duty_cycle_servo = pwm_chip_servo + "/pwm2/duty_cycle"
pwm_enable_servo = pwm_chip_servo + "/pwm2/enable"

# Lokasi PWM untuk motor (pwm1) di sysfs
pwm_chip_motor = "/sys/class/pwm/pwmchip0"
pwm_export_motor = pwm_chip_motor + "/export"
pwm_unexport_motor = pwm_chip_motor + "/unexport"
pwm_period_motor = pwm_chip_motor + "/pwm1/period"
pwm_duty_cycle_motor = pwm_chip_motor + "/pwm1/duty_cycle"
pwm_enable_motor = pwm_chip_motor + "/pwm1/enable"

# URL API untuk mengirim dan menerima kecepatan
api_url_motor = "http://192.168.125.137:9000/v1/control/"  # Ganti dengan URL API yang benar

# Fungsi untuk menginisialisasi PWM untuk motor
def init_pwm_motor():
    # Ekspor PWM1 jika belum diekspor
    try:
        with open(pwm_export_motor, 'w') as f:
            f.write("1")
    except FileExistsError:
        pass
    
    # Set period (contoh: 20ms untuk motor)
    with open(pwm_period_motor, 'w') as f:
        f.write("20000000")  # 20 ms

    # Aktifkan PWM1 untuk motor
    with open(pwm_enable_motor, 'w') as f:
        f.write("1")

# Fungsi untuk menginisialisasi PWM untuk servo
def init_pwm_servo():
    # Ekspor PWM2 jika belum diekspor
    try:
        with open(pwm_export_servo, 'w') as f:
            f.write("2")
    except FileExistsError:
        pass
    
    # Set period (contoh: 20ms untuk servo)
    with open(pwm_period_servo, 'w') as f:
        f.write("20000000")  # 20 ms

    # Aktifkan PWM2 untuk servo
    with open(pwm_enable_servo, 'w') as f:
        f.write("1")

# Fungsi untuk mengatur kecepatan motor
def set_motor_speed(speed):
    if speed < 0 or speed > 100:
        raise ValueError("Kecepatan harus antara 0 dan 100 persen")
    
    min_duty_cycle = 1200000  # 1.2ms (untuk kecepatan 0%)
    max_duty_cycle = 2000000  # 2ms (untuk kecepatan 100%)

    duty_cycle = min_duty_cycle + (speed / 100.0) * (max_duty_cycle - min_duty_cycle)
    print(f"Setting motor duty cycle: {duty_cycle} ns for speed {speed}%")
    with open(pwm_duty_cycle_motor, 'w') as f:
        f.write(str(int(duty_cycle)))

    # Kirim feedback kecepatan ke API
    send_speed_feedback_motor(speed)

# Fungsi untuk mengirim feedback kecepatan motor ke API
def send_speed_feedback_motor(speed):
    params = {'speed': speed}
    try:
        response = requests.get(api_url_motor, params=params)
        if response.status_code == 200:
            print(f"Kecepatan {speed}% berhasil dikirim ke API")
        else:
            print(f"Error mengirim kecepatan ke API: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Gagal mengirim data ke API: {e}")

# Fungsi untuk menonaktifkan PWM motor
def disable_pwm_motor():
    with open(pwm_enable_motor, 'w') as f:
        f.write("0")
    with open(pwm_unexport_motor, 'w') as f:
        f.write("1")

# Fungsi untuk menonaktifkan PWM servo
def disable_pwm_servo():
    with open(pwm_enable_servo, 'w') as f:
        f.write("0")
    with open(pwm_unexport_servo, 'w') as f:
        f.write("2")

# Fungsi untuk mendapatkan kecepatan dari API untuk motor
def get_speed_from_api_motor():
    try:
        response = requests.get(api_url_motor)
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
    async with websockets.connect("ws://192.168.125.137:9999/sender") as websocket:
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

# Fungsi utama untuk menjalankan kontrol motor
async def pwm_motor_control_loop():
    try:
        init_pwm_motor()
        while True:
            speed = get_speed_from_api_motor()
            if speed is not None:
                set_motor_speed(speed)
            await asyncio.sleep(1)  # Tunggu 1 detik sebelum cek lagi
    except KeyboardInterrupt:
        print("Program PWM motor dihentikan")
    except ValueError as e:
        print(e)
    finally:
        disable_pwm_motor()

# Fungsi utama untuk menjalankan kontrol servo
async def pwm_servo_control_loop():
    try:
        init_pwm_servo()
        # Servo loop dapat disesuaikan dengan API yang diinginkan
        await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Program PWM servo dihentikan")
    finally:
        disable_pwm_servo()

# Fungsi untuk menjalankan semua tugas secara bersamaan
async def main():
    await asyncio.gather(
        send_images(),
        pwm_motor_control_loop(),
        pwm_servo_control_loop()
    )

# Jalankan event loop asyncio untuk semua tugas
asyncio.get_event_loop().run_until_complete(main())
