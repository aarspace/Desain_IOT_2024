import OPi.GPIO as GPIO
import time

# Setup mode GPIO
GPIO.setmode(GPIO.BOARD)  # Menggunakan nomor pin fisik pada header (board numbering)
GPIO.setup(19, GPIO.OUT)  # Pin 11 (GPIO17) sebagai output (PWM pin)

# Setup PWM pada pin 11 (GPIO17)
pwm = GPIO.PWM(19, 50)  # PWM dengan frekuensi 50Hz (frekuensi standar servo motor)
pwm.start(0)  # Mulai PWM dengan duty cycle 0%

def set_angle(angle):
    # Menghitung duty cycle untuk menentukan posisi servo
    duty = angle / 18 + 2
    GPIO.output(11, True)  # Mengaktifkan PWM
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)  # Berikan waktu untuk servo bergerak
    GPIO.output(11, False)  # Matikan PWM

try:
    # Tes pergerakan servo ke berbagai sudut
    while True:
        for angle in range(0, 180, 10):  # Gerakkan servo dari 0 hingga 180 derajat
            print(f"Set angle to {angle} degrees")
            set_angle(angle)
            time.sleep(1)
        for angle in range(180, 0, -10):  # Gerakkan servo kembali ke 0 derajat
            print(f"Set angle to {angle} degrees")
            set_angle(angle)
            time.sleep(1)

except KeyboardInterrupt:
    print("Program berhenti")
    pwm.stop()  # Hentikan PWM
    GPIO.cleanup()  # Bersihkan pengaturan GPIO
