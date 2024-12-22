import OPi.GPIO as GPIO
import time

def main():
    print("Menginisialisasi PWM...")

    # Set up GPIO
    GPIO.setmode(GPIO.BOARD)  # Atur nomor pin berdasarkan board
    PWM_chip = 0              # Chip PWM (biasanya 0 pada Orange Pi)
    PWM_pin = 1               # Pin yang digunakan (misalnya pin 1, sesuaikan dengan pin yang Anda gunakan)
    frequency_Hz = 50       # Frekuensi PWM, sesuaikan dengan kebutuhan motor (misalnya 3800Hz)
    duty_cycle_percent = 0    # Mulai dengan duty cycle 0%

    try:
        pwm = GPIO.PWM(PWM_chip, PWM_pin, frequency_Hz, duty_cycle_percent)
        pwm.start_pwm()  # Mulai PWM
        print(f"PWM dimulai dengan frekuensi {frequency_Hz}Hz dan duty cycle {duty_cycle_percent}%.")

        # Pengaturan Duty Cycle secara interaktif
        while True:
            print("\nPilih aksi:")
            print("1. Kecepatan Penuh (Duty Cycle 100%)")
            print("2. Setengah Kecepatan (Duty Cycle 50%)")
            print("3. Kecepatan Minimum (Duty Cycle 0%)")
            print("4. Keluar")

            action = input("Masukkan pilihan: ")

            if action == "1":
                print("Mengatur Duty Cycle ke 100% (Kecepatan Penuh).")
                pwm.duty_cycle(100)  # Set duty cycle ke 100%
            elif action == "2":
                print("Mengatur Duty Cycle ke 50%.")
                pwm.duty_cycle(50)   # Set duty cycle ke 50%
            elif action == "3":
                print("Mengatur Duty Cycle ke 0% (Motor Mati).")
                pwm.duty_cycle(0)    # Set duty cycle ke 0% (motor mati)
            elif action == "4":
                print("Keluar dari program.")
                break
            else:
                print("Pilihan tidak valid.")

            time.sleep(1)  # Tunggu 1 detik sebelum menerima input berikutnya

    except Exception as e:
        print(f"Terjadi error: {e}")
    
    finally:
        print("Menutup PWM dan GPIO...")
        pwm.stop_pwm()   # Matikan PWM
        pwm.pwm_close()  # Tutup pin PWM
        GPIO.cleanup()   # Bersihkan konfigurasi GPIO

if __name__ == "__main__":
    main()
