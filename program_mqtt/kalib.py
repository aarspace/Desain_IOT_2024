import OPi.GPIO as GPIO
import time

def initialize_esc(pwm):
    """Inisialisasi ESC dengan sinyal netral"""
    print("Menginisialisasi ESC dengan sinyal netral...")
    pwm.duty_cycle(7.5)  # Posisi netral (~1.5 ms pulsa)
    time.sleep(2)        # Tunggu beberapa detik untuk inisialisasi ESC

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
                pwm.duty_cycle(10)  # Set duty cycle untuk kecepatan penuh
            elif action == "2":
                print("Mengatur Duty Cycle ke ~8% (Setengah Kecepatan).")
                pwm.duty_cycle(8)   # Set duty cycle untuk setengah kecepatan
            elif action == "3":
                print("Mengatur Duty Cycle ke ~6% (Motor Mati).")
                pwm.duty_cycle(6)   # Set duty cycle untuk berhenti
            elif action == "4":
                print("Mengatur Duty Cycle ke ~7.5% (Netral).")
                pwm.duty_cycle(7.5)  # Set duty cycle ke netral
            elif action == "5":
                print("Keluar dari program.")
                break
            else:
                print("Pilihan tidak valid.")

            time.sleep(1)  # Tunggu 1 detik sebelum menerima input berikutnya

    except Exception as e:
        print(f"Terjadi error: {e}")
    
    finally:
        print("Menutup PWM dan GPIO...")
        if pwm:  # Pastikan pwm telah diinisialisasi sebelum mencoba mematikannya
            pwm.stop_pwm()   # Matikan PWM
            pwm.pwm_close()  # Tutup pin PWM
        GPIO.cleanup()       # Bersihkan konfigurasi GPIO

if __name__ == "__main__":
    main()
