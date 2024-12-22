import OPi.GPIO as GPIO
import time

def calibrate_esc(pwm):
    """
    Kalibrasi ESC.
    - Mengatur sinyal PWM maksimum (10%) untuk mengatur batas atas.
    - Mengatur sinyal PWM minimum (6%) untuk mengatur batas bawah.
    """
    print("Memulai proses kalibrasi ESC...")
    print("Langkah 1: Mengatur sinyal maksimum (10%)...")
    pwm.duty_cycle(10)  # Sinyal maksimum (~2 ms pulsa)
    time.sleep(2)       # Tahan selama 2 detik

    print("Langkah 2: Mengatur sinyal minimum (6%)...")
    pwm.duty_cycle(6)   # Sinyal minimum (~1 ms pulsa)
    time.sleep(2)       # Tahan selama 2 detik

    print("Kalibrasi selesai! Kembali ke posisi netral (~7.5%)...")
    pwm.duty_cycle(7.5) # Posisi netral (~1.5 ms pulsa)
    time.sleep(1)       # Tunggu sebentar untuk memastikan posisi netral diterima
    print("ESC siap digunakan.")

def main():
    print("Menginisialisasi PWM untuk kalibrasi ESC...")

    # Setup GPIO
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

        # Jalankan kalibrasi
        calibrate_esc(pwm)

        print("Tekan Ctrl+C untuk keluar atau ESC akan tetap dalam mode netral.")
        while True:
            time.sleep(1)  # Tetap dalam mode netral

    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")
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
