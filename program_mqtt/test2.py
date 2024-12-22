import OPi.GPIO as GPIO
import time

def main():
    print("Menginisialisasi PWM...")

    # Setup GPIO
    GPIO.setmode(GPIO.BOARD)  # Gunakan nomor pin berdasarkan board
    PWM_pin = 1             # Sesuaikan pin PWM (misalnya, pin 12 BOARD mode)
    frequency_Hz = 50        # Frekuensi PWM untuk ESC (biasanya 50Hz)
    duty_cycle_percent = 7.5 # Duty cycle untuk posisi netral ESC (7.5% = 1.5ms)

    pwm = None  # Inisialisasi awal variabel pwm

    try:
        GPIO.setup(PWM_pin, GPIO.OUT)
        pwm = GPIO.PWM(PWM_pin, frequency_Hz)
        pwm.start(duty_cycle_percent)  # Mulai PWM dengan posisi netral
        print(f"PWM dimulai dengan frekuensi {frequency_Hz}Hz dan duty cycle {duty_cycle_percent}%.")

        # Pengaturan Duty Cycle secara interaktif
        while True:
            print("\nPilih aksi:")
            print("1. Kecepatan Penuh (Duty Cycle ~10%)")
            print("2. Setengah Kecepatan (Duty Cycle ~8%)")
            print("3. Kecepatan Minimum (Duty Cycle ~6%)")
            print("4. Keluar")

            action = input("Masukkan pilihan: ")

            if action == "1":
                print("Mengatur Duty Cycle ke 10% (Kecepatan Penuh).")
                pwm.ChangeDutyCycle(10)  # Set duty cycle untuk kecepatan penuh
            elif action == "2":
                print("Mengatur Duty Cycle ~8% (Setengah Kecepatan).")
                pwm.ChangeDutyCycle(8)   # Set duty cycle untuk setengah kecepatan
            elif action == "3":
                print("Mengatur Duty Cycle ke ~6% (Motor Mati).")
                pwm.ChangeDutyCycle(6)   # Set duty cycle untuk berhenti
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
        if pwm:  # Hanya eksekusi jika pwm berhasil diinisialisasi
            pwm.stop()       # Matikan PWM
        GPIO.cleanup()       # Bersihkan konfigurasi GPIO

if __name__ == "__main__":
    main()
