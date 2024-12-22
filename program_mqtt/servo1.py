import time
import OPi.GPIO as GPIO

# Fungsi untuk mengonversi sudut (0-180) ke duty cycle (1 ms - 2 ms)
def angle_to_duty_cycle(angle):
    """Mengonversi sudut (0-180) ke duty cycle (1ms - 2ms) untuk motor servo"""
    # 0 derajat -> 1 ms (duty cycle sekitar 5%)
    # 180 derajat -> 2 ms (duty cycle sekitar 10%)
    duty_cycle = 4 + (angle / 180) * 7  # 5% duty cycle untuk 0 derajat dan 10% untuk 180 derajat
    return duty_cycle

def calibrate_servo(pwm):
    """Kalibrasi servo ke sudut 0 dan 180 derajat"""
    print("Memulai kalibrasi servo...")

    # Menggerakkan servo ke sudut 0 derajat
    print("Posisi 0 derajat...")
    pwm.duty_cycle(angle_to_duty_cycle(0))
    time.sleep(2)

    # Menggerakkan servo ke sudut 180 derajat
    print("Posisi 180 derajat...")
    pwm.duty_cycle(angle_to_duty_cycle(180))
    time.sleep(2)

    # Kembali ke posisi 90 derajat
    print("Posisi 90 derajat (netral)...")
    pwm.duty_cycle(angle_to_duty_cycle(90))
    time.sleep(1)

    print("Kalibrasi selesai! Servo siap digunakan.")

def main():
    print("Menginisialisasi PWM untuk kontrol servo...")

    # Setup GPIO
    GPIO.setmode(GPIO.BOARD)  # Atur nomor pin berdasarkan board
    PWM_chip = 0              # Chip PWM (biasanya 0 pada Orange Pi)
    PWM_pin = 2               # Pin yang digunakan (sesuaikan dengan pin yang Anda gunakan)
    frequency_Hz = 50         # Frekuensi PWM untuk servo (50 Hz)
    duty_cycle_percent = 7.5  # Mulai dengan posisi netral (~1.5 ms pulsa)

    pwm = None  # Inisialisasi variabel PWM

    try:
        # Konfigurasi PWM
        pwm = GPIO.PWM(PWM_chip, PWM_pin, frequency_Hz, duty_cycle_percent)
        pwm.start_pwm()  # Mulai PWM dengan duty cycle awal
        print(f"PWM dimulai pada frekuensi {frequency_Hz}Hz dengan duty cycle {duty_cycle_percent}%.")

        # Kalibrasi servo
        calibrate_servo(pwm)

        # Pengaturan sudut secara interaktif
        while True:
            try:
                # Input sudut dari pengguna
                angle = int(input("\nMasukkan sudut (0-180 derajat): "))

                if 0 <= angle <= 180:
                    # Mengatur posisi servo sesuai dengan sudut yang dimasukkan
                    duty_cycle = angle_to_duty_cycle(angle)
                    pwm.duty_cycle(duty_cycle)
                    print(f"Servo bergerak ke {angle} derajat dengan duty cycle {duty_cycle:.2f}%")
                else:
                    print("Masukkan sudut antara 0 dan 180 derajat.")

            except ValueError:
                print("Masukkan nilai yang valid (angka).")

            time.sleep(1)  # Tunggu 1 detik sebelum menerima input berikutnya

    except Exception as e:
        print(f"Terjadi error: {e}")
    
    finally:
        print("Menutup PWM dan GPIO...")
        if pwm:  # Pastikan pwm telah diinisialisasi sebelum mencoba mematikannya
            pwm.duty_cycle(0)  # Matikan motor dengan duty cycle 0%
            pwm.stop_pwm()     # Matikan PWM
            pwm.pwm_close()    # Tutup pin PWM
        GPIO.cleanup()         # Bersihkan konfigurasi GPIO
        print("PWM dimatikan, GPIO bersih.")

if __name__ == "__main__":
    main()
