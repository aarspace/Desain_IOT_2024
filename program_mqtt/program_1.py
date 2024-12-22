import time
import asyncio
import cv2
import websockets
import paho.mqtt.client as mqtt

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

# Konfigurasi MQTT
mqtt_broker = "3.129.58.174"  # Ganti dengan alamat broker MQTT
mqtt_port = 1883
mqtt_topic_motor = "motor/speed"
mqtt_topic_servo = "servo/angle"

# Fungsi untuk menginisialisasi PWM untuk motor
def init_pwm_motor():
    try:
        with open(pwm_export_motor, 'w') as f:
            f.write("1")
    except FileExistsError:
        pass
    
    with open(pwm_period_motor, 'w') as f:
        f.write("20000000")  # 20 ms

    with open(pwm_enable_motor, 'w') as f:
        f.write("1")

# Fungsi untuk menginisialisasi PWM untuk servo
def init_pwm_servo():
    try:
        with open(pwm_export_servo, 'w') as f:
            f.write("2")
    except FileExistsError:
        pass
    
    with open(pwm_period_servo, 'w') as f:
        f.write("20000000")  # 20 ms

    with open(pwm_enable_servo, 'w') as f:
        f.write("1")

# Fungsi untuk mengatur kecepatan motor
def set_motor_speed(speed):
    if speed < 0 or speed > 100:
        raise ValueError("Kecepatan harus antara 0 dan 100 persen")
    
    min_duty_cycle = 1200000
    max_duty_cycle = 2000000

    duty_cycle = min_duty_cycle + (speed / 100.0) * (max_duty_cycle - min_duty_cycle)
    print(f"Setting motor duty cycle: {duty_cycle} ns for speed {speed}%")
    with open(pwm_duty_cycle_motor, 'w') as f:
        f.write(str(int(duty_cycle)))

# Fungsi untuk mengatur sudut servo
def set_servo_angle(angle):
    if angle < 0 or angle > 180:
        raise ValueError("Sudut harus antara 0 dan 180 derajat")
    
    min_duty_cycle = 500000  # 0.5ms untuk sudut 0 derajat
    max_duty_cycle = 2500000  # 2.5ms untuk sudut 180 derajat

    duty_cycle = min_duty_cycle + (angle / 180.0) * (max_duty_cycle - min_duty_cycle)
    print(f"Setting servo duty cycle: {duty_cycle} ns for angle {angle}°")
    with open(pwm_duty_cycle_servo, 'w') as f:
        f.write(str(int(duty_cycle)))

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

# Callback untuk MQTT
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    
    try:
        if topic == mqtt_topic_motor:
            speed = float(payload)
            set_motor_speed(speed)
        elif topic == mqtt_topic_servo:
            angle = float(payload)
            set_servo_angle(angle)
    except ValueError as e:
        print(f"Invalid data received on topic {topic}: {e}")

# Fungsi untuk menghubungkan dan menjalankan MQTT
def run_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(mqtt_broker, mqtt_port)
    client.subscribe([(mqtt_topic_motor, 0), (mqtt_topic_servo, 0)])
    client.loop_forever()

# Fungsi untuk mengirimkan gambar melalui WebSocket
async def send_images():
    async with websockets.connect("ws://3.129.58.174:8083/mqtt") as websocket:
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

# Fungsi utama
async def main():
    init_pwm_motor()
    init_pwm_servo()
    
    try:
        await asyncio.gather(
            asyncio.to_thread(run_mqtt),
            send_images()
        )
    finally:
        disable_pwm_motor()
        disable_pwm_servo()

# Jalankan event loop asyncio
asyncio.run(main())
