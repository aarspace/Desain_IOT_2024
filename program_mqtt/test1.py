import OPi.GPIO as GPIO

def main():
    try:
        # Bersihkan konfigurasi sebelumnya
        GPIO.cleanup()

        # Konfigurasi PWM
        PWM_chip = 0
        PWM_pin = 1  # Gunakan pin yang mendukung PWM
        frequency_Hz = 50000  # Frekuensi standar untuk ESC
        duty_cycle_percent = 100  # Nilai netral

        # Inisialisasi PWM
        print("Menginisialisasi PWM...")
        pwm = GPIO.PWM(PWM_chip, PWM_pin, frequency_Hz, duty_cycle_percent)
        pwm.start_pwm()
        print(f"PWM aktif di pin {PWM_pin} dengan frekuensi {frequency_Hz} Hz dan duty cycle {duty_cycle_percent}%.")

        # Kontrol PWM
        while True:
            print("\nPilih opsi:")
            print("1. Naikkan duty cycle (kecepatan motor bertambah)")
            print("2. Turunkan duty cycle (kecepatan motor berkurang)")
            print("3. Stop PWM")
            print("4. Keluar")
            choice = input("Masukkan pilihan Anda: ")

            if choice == "1":
                duty_cycle_percent += 2.5
                if duty_cycle_percent > 12.5:
                    duty_cycle_percent = 12.5
                pwm.duty_cycle(duty_cycle_percent)
                print(f"Duty cycle ditingkatkan ke {duty_cycle_percent}%.")

            elif choice == "2":
                duty_cycle_percent -= 2.5
                if duty_cycle_percent < 5:
                    duty_cycle_percent = 5
                pwm.duty_cycle(duty_cycle_percent)
                print(f"Duty cycle diturunkan ke {duty_cycle_percent}%.")

            elif choice == "3":
                pwm.stop_pwm()
                print("PWM dihentikan.")

            elif choice == "4":
                print("Keluar program.")
                break

            else:
                print("Pilihan tidak valid. Coba lagi.")

    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")

    except Exception as e:
        print(f"Terjadi error: {e}")

    finally:
        if 'pwm' in locals():
            pwm.stop_pwm()
            pwm.pwm_close()
            del pwm
        GPIO.cleanup()
        print("PWM dinonaktifkan. Selesai.")

if __name__ == "__main__":
    main()
