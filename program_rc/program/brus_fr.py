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

# Fungsi untuk mengatur kecepatan motor dan arah putaran
def set_motor_speed_and_direction(speed, direction):
    # Validasi input kecepatan (0-100%)
    if speed < 0 or speed > 100:
        raise ValueError("Kecepatan harus antara 0 dan 100 persen")

    # Kalibrasi rentang duty cycle
    # Untuk putaran maju (1.5ms ke atas)
    if direction == "forward":
        min_duty_cycle = 1500000  # 1.5ms (untuk kecepatan 0%)
        max_duty_cycle = 2000000  # 2ms (untuk kecepatan 100%)

    # Untuk putaran mundur (1.5ms ke bawah)
    elif direction == "reverse":
        min_duty_cycle = 1000000  # 1ms (untuk kecepatan mundur maksimum)
        max_duty_cycle = 1500000  # 1.5ms (untuk kecepatan 0%)

    # Hitung duty cycle berdasarkan kecepatan (%)
    duty_cycle = min_duty_cycle + (speed / 100.0) * (max_duty_cycle - min_duty_cycle)
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
            # Input arah dan kecepatan dari pengguna
            direction = input("Masukkan arah (forward/reverse): ").strip().lower()
            speed = float(input("Masukkan kecepatan motor (0-100%): "))
            set_motor_speed_and_direction(speed, direction)
            time.sleep(1)  # Beri waktu untuk motor merespon

    except KeyboardInterrupt:
        print("Program dihentikan")
    except ValueError as e:
        print(e)
    finally:
        disable_pwm()
