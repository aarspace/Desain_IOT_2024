import time
import OPi.GPIO as GPIO

def initialize_esc(pwm):
    """Inisialisasi ESC dengan sinyal netral"""
    print("Menginisialisasi ESC dengan sinyal netral...")
    pwm.duty_cycle(7.5)  # Posisi netral (~1.5 ms pulsa)
    time.sleep(2)        # Tunggu beberapa detik untuk inisialisasi ESC

def gradual_duty_cycle(pwm, start, end, step=0.5, delay=0.1):
    """Ubah duty cycle secara bertahap untuk menghindari penghentian mendadak oleh ESC."""
    if start < end:
        duty = start
        while duty <= end:
            pwm.duty_cycle(duty)
            time.sleep(delay)
            duty += step
    elif start > end:
        duty = start
        while duty >= end:
            pwm.duty_cycle(duty)
            time.sleep(delay)
            duty -= step

def main():
    print("Menginisialisasi PWM dan ESC...")

    # Set up GPIO
    GPIO.setmode(GPIO.BOARD)  # Atur nomor pin berdasarkan board
    PWM_chip = 0              # Chip PWM (biasanya 0 pada Orange Pi)
    PWM_pin = 1               # Pin yang digunakan (sesuaikan dengan pin yang Anda gunakan)
    frequency_Hz = 50         # Frekuensi PWM untuk ESC
    duty_cycle_percent = 7.5  # Mulai dengan duty cycle netral

    pwm = None  # Inisialisasi variabel PWM

    try:
        # Konfigurasi PWM
        pwm = GPIO.PWM(PWM_chip, PWM_pin, frequency_Hz, duty_cycle_percent)
        pwm.start_pwm()  # Mulai PWM dengan duty cycle awal
        print(f"PWM dimulai pada frekuensi {frequency_Hz}Hz dengan duty cycle {duty_cycle_percent}%.")

        # Inisialisasi ESC
        initialize_esc(pwm)

        # Pengaturan Duty Cycle secara interaktif
        while True:
            print("\nPilih aksi:")
            print("1. Kecepatan Penuh (Duty Cycle ~10%)")
            print("2. Setengah Kecepatan (Duty Cycle ~8%)")
            print("3. Kecepatan Minimum (Duty Cycle ~6%)")
            print("4. Netral (Duty Cycle ~7.5%)")
            print("5. Keluar")

            action = input("Masukkan pilihan: ")

            if action == "1":
                print("Mengatur Duty Cycle ke 10% (Kecepatan Penuh).")
                gradual_duty_cycle(pwm, duty_cycle_percent, 10)
                duty_cycle_percent = 10
            elif action == "2":
                print("Mengatur Duty Cycle ke ~8% (Setengah Kecepatan).")
                gradual_duty_cycle(pwm, duty_cycle_percent, 8)
                duty_cycle_percent = 8
            elif action == "3":
                print("Mengatur Duty Cycle ke ~6% (Motor Mati).")
                gradual_duty_cycle(pwm, duty_cycle_percent, 6)
                duty_cycle_percent = 6
            elif action == "4":
                print("Mengatur Duty Cycle ke ~7.5% (Netral).")
                gradual_duty_cycle(pwm, duty_cycle_percent, 7.5)
                duty_cycle_percent = 7.5
            elif action == "5":
                print("Keluar dari program.")
                break
            else:
                print("Pilihan tidak valid.")

    except Exception as e:
        print(f"Terjadi error: {e}")
    
    finally:
        print("Menutup PWM dan GPIO...")
        if pwm:  # Pastikan pwm telah diinisialisasi sebelum mencoba mematikannya
            pwm.duty_cycle(0)  # Matikan motor dengan duty cycle 0%
            pwm.stop_pwm()     # Matikan PWM
            pwm.pwm_close()    # Tutup pin PWM
        GPIO.cleanup()         # Bersihkan konfigurasi GPIO
        print("Motor berhenti.")

if __name__ == "__main__":
    main()
