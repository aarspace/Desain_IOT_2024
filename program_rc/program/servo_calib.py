import time

# Lokasi PWM di sysfs
pwm_chip = "/sys/class/pwm/pwmchip0"
pwm_export = pwm_chip + "/export"
pwm_unexport = pwm_chip + "/unexport"
pwm_period = pwm_chip + "/pwm2/period"
pwm_duty_cycle = pwm_chip + "/pwm2/duty_cycle"
pwm_enable = pwm_chip + "/pwm2/enable"

# Fungsi untuk menginisialisasi PWM
def init_pwm():
    # Ekspor PWM jika belum diekspor
    try:
        with open(pwm_export, 'w') as f:
            f.write("1")
    except FileExistsError:
        # PWM sudah diekspor, lewati
        pass
    
    # Set period (contoh: 20ms untuk servo)
    with open(pwm_period, 'w') as f:
        f.write("20000000")  # 20 ms

    # Aktifkan PWM
    with open(pwm_enable, 'w') as f:
        f.write("1")

# Fungsi untuk mengatur sudut servo (dalam derajat)
def set_servo_angle(angle):
    # Validasi input sudut (0-90 derajat)
    if angle < 0 or angle > 90:
        raise ValueError("Sudut harus antara 0 dan 90 derajat")
    
    # Kalibrasi rentang duty cycle
    min_duty_cycle = 1000000  # 1ms (untuk sudut 0)
    max_duty_cycle = 2000000   # 1.5ms (untuk sudut 90) - ubah jika diperlukan
    #     max_duty_cycle = 2400000   # 1.5ms (untuk sudut 90) - ubah jika diperlukan hampir 180

    # Hitung duty cycle untuk sudut tertentu
    duty_cycle = min_duty_cycle + (angle / 90.0) * (max_duty_cycle - min_duty_cycle)
    with open(pwm_duty_cycle, 'w') as f:
        f.write(str(int(duty_cycle)))

# Fungsi untuk menonaktifkan PWM
def disable_pwm():
    with open(pwm_enable, 'w') as f:
        f.write("0")
    with open(pwm_unexport, 'w') as f:
        f.write("1")

if __name__ == "__main__":
    try:
        init_pwm()
        while True:
            # Input sudut dari pengguna
            angle = float(input("Masukkan sudut servo (0-90 derajat): "))
            set_servo_angle(angle)
            time.sleep(1)  # Beri waktu untuk servo bergerak

    except KeyboardInterrupt:
        print("Program dihentikan")
    except ValueError as e:
        print(e)
    finally:
        disable_pwm()
