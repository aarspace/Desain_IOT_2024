import wiringpi

OUTPUT = 1
PIN_TO_PWM = 6  # Ganti dengan nomor pin yang sesuai untuk PWM di perangkat Anda

# Setup GPIO untuk menggunakan wiringPi
wiringpi.wiringPiSetup()

# Set pin untuk output
wiringpi.pinMode(PIN_TO_PWM, OUTPUT)

# Setup PWM pada pin, nilai awal 0 dan range 0-100 (duty cycle)
wiringpi.softPwmCreate(PIN_TO_PWM, 0, 100)

# Loop untuk mengubah brightness secara bertahap
for cycle in range(0, 4):  # Mengulangi 4 kali untuk mencerahkan dan meredupkan LED
    # Meningkatkan kecerahan dari 0 ke 100
    for brightness in range(0, 100):
        print(f"Cycle {cycle + 1}: Increasing brightness to {brightness}")
        wiringpi.softPwmWrite(PIN_TO_PWM, brightness)  # Atur PWM duty cycle
        wiringpi.delay(10)  # Delay untuk memberikan efek
    # Mengurangi kecerahan dari 100 ke 0
    for brightness in reversed(range(0, 100)):
        print(f"Cycle {cycle + 1}: Decreasing brightness to {brightness}")
        wiringpi.softPwmWrite(PIN_TO_PWM, brightness)  # Atur PWM duty cycle
        wiringpi.delay(10)  # Delay untuk memberikan efek
