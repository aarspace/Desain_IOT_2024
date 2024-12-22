import paho.mqtt.client as mqtt
import time

# Konfigurasi MQTT
mqtt_broker = "3.129.58.174"  # Ganti dengan alamat broker MQTT
mqtt_port = 1883
mqtt_topic_motor = "motor/speed"
mqtt_topic_servo = "servo/angle"

# Fungsi untuk mengirim data ke MQTT
def publish_data():
    # Inisialisasi klien MQTT
    client = mqtt.Client()
    client.connect(mqtt_broker, mqtt_port)

    try:
        while True:
            # Kirim data kecepatan motor
            motor_speed = input("Masukkan kecepatan motor (0-100%): ")
            if motor_speed.isdigit() and 0 <= int(motor_speed) <= 100:
                client.publish(mqtt_topic_motor, motor_speed)
                print(f"Dikirim: {motor_speed}% kecepatan motor ke topik {mqtt_topic_motor}")
            else:
                print("Kecepatan harus angka antara 0-100!")

            # Kirim data sudut servo
            servo_angle = input("Masukkan sudut servo (0-180 derajat): ")
            if servo_angle.isdigit() and 0 <= int(servo_angle) <= 180:
                client.publish(mqtt_topic_servo, servo_angle)
                print(f"Dikirim: {servo_angle}° sudut servo ke topik {mqtt_topic_servo}")
            else:
                print("Sudut harus angka antara 0-180!")

            time.sleep(1)  # Tunggu sebelum mengirim data berikutnya
    except KeyboardInterrupt:
        print("Program dihentikan.")
    finally:
        client.disconnect()

if __name__ == "__main__":
    publish_data()
