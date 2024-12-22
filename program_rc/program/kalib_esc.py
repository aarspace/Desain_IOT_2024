import time

# Lokasi PWM di sysfs
pwm_chip = "/sys/class/pwm/pwmchip0"
pwm_export = pwm_chip + "/export"
pwm_unexport = pwm_chip + "/unexport"
pwm_period = pwm_chip + "/pwm1/period"
pwm_duty_cycle = pwm_chip + "/pwm1/duty_cycle"
pwm_enable = pwm_chip + "/pwm1/enable"

# Fungsi untuk menginisialisasi PWM
def init_pwm():
    # Ekspor PWM jika belum diekspor
    try:
        with open(pwm_export, 'w') as f:
            f.write("1")
    except FileExistsError:
        pass
    
    # Set period (contoh: 20ms untuk ESC)
    with open(pwm_period, 'w') as f:
        f.write("20000000")  # 20 ms

    # Aktifkan PWM
    with open(pwm_enable, 'w') as f:
        f.write("1")

# Fungsi untuk mengatur duty cycle PWM
def set_pwm_duty_cycle(duty_cycle):
    print(f"Setting duty cycle: {duty_cycle} ns")
    with open(pwm_duty_cycle, 'w') as f:
        f.write(str(int(duty_cycle)))

# Fungsi untuk mengkalibrasi ESC
def calibrate_esc():
    try:
        init_pwm()
        
        print("Memulai kalibrasi ESC...")
        
        # Step 1: Sinyal maksimum (100%)
        print("Mengirim sinyal maksimum (100%)...")
        set_pwm_duty_cycle(2000000)  # 2 ms untuk sinyal maksimum
        time.sleep(3)  # Tunggu 3 detik
        
        # Step 2: Sinyal minimum (0%)
        print("Mengirim sinyal minimum (0%)...")
        set_pwm_duty_cycle(1000000)  # 1 ms untuk sinyal minimum
        time.sleep(3)  # Tunggu 3 detik
        
        # Step 3: Sinyal stabil di tengah (50%)
        print("Mengirim sinyal stabil di tengah (50%)...")
        set_pwm_duty_cycle(1500000)  # 1.5 ms untuk sinyal stabil
        time.sleep(3)
        
        print("Kalibrasi selesai. Motor siap digunakan.")
    
    except Exception as e:
        print(f"Terjadi kesalahan saat kalibrasi: {e}")
    
    finally:
        disable_pwm()

# Fungsi untuk menonaktifkan PWM
def disable_pwm():
    with open(pwm_enable, 'w') as f:
        f.write("0")
    with open(pwm_unexport, 'w') as f:
        f.write("1")

if __name__ == "__main__":
    try:
        calibrate_esc()
    except KeyboardInterrupt:
        print("Kalibrasi dihentikan.")
    finally:
        disable_pwm()
