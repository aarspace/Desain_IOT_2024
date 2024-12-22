import OPi.GPIO as GPIO
import time

def main():
    print("Menginisialisasi PWM untuk kecepatan penuh...")

    # Setup GPIO
    GPIO.setmode(GPIO.BOARD)  # Atur nomor pin berdasarkan board
    PWM_chip = 0              # Chip PWM (biasanya 0 pada Orange Pi)
    PWM_pin = 1               # Pin yang digunakan (sesuaikan dengan pin yang Anda gunakan)
    frequency_Hz = 50         # Frekuensi PWM untuk ESC
    duty_cycle_percent = 10   # Duty cycle untuk kecepatan penuh (~2 ms pulsa)

    pwm = None  # Inisialisasi variabel PWM

    try:
        # Konfigurasi PWM
        pwm = GPIO.PWM(PWM_chip, PWM_pin, frequency_Hz, duty_cycle_percent)
        pwm.start_pwm()  # Mulai PWM
        print(f"Motor berjalan pada kecepatan penuh dengan frekuensi {frequency_Hz}Hz dan duty cycle {duty_cycle_percent}%.")

        print("Tekan Ctrl+C untuk menghentikan program.")
        while True:
            time.sleep(1)  # Loop untuk menjaga program tetap berjalan

    except KeyboardInterrupt:
        # Jika pengguna menekan Ctrl+C, kita akan keluar dengan aman
        print("\nProgram dihentikan oleh pengguna.")
    except Exception as e:
        print(f"Terjadi error: {e}")
    
    finally:
        # Bersihkan GPIO dan matikan motor
        print("Menutup PWM dan menghentikan motor...")
        if pwm:  # Pastikan pwm telah diinisialisasi sebelum mencoba mematikannya
            pwm.duty_cycle(0)  # Matikan motor dengan duty cycle 0%
            pwm.stop_pwm()     # Matikan PWM
            pwm.pwm_close()    # Tutup pin PWM
        GPIO.cleanup()         # Bersihkan konfigurasi GPIO
        print("Motor berhenti.")

if __name__ == "__main__":
    main()
