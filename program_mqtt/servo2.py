import OPi.GPIO as GPIO
import time

# Set GPIO mode to SUNXI for Orange Pi
GPIO.setmode(GPIO.SUNXI)
GPIO.setwarnings(False)
# Define the pin for the servo (e.g., PC11)
servo_pin = "PC11"

# Setup pin as output
GPIO.setup(servo_pin, GPIO.OUT)

# Initialize PWM on the pin with frequency 50Hz
pwm = GPIO.PWM(servo_pin, 50)  # Initialize PWM with 50Hz frequency

# Start PWM with an initial duty cycle of 0% (servo at rest position)
pwm.start(0)  # Duty cycle set to 0%

# Function to set servo angle (0 to 180 degrees)
def set_angle(angle):
    # Map the angle (0-180) to a duty cycle (2%-12%)
    duty = (angle / 18) + 2  # Converts angle to a duty cycle between 2% and 12%
    pwm.ChangeDutyCycle(duty)  # Change PWM duty cycle to control the servo position
    time.sleep(0.5)  # Give time for the servo to move to the position

try:
    while True:
        # Sweep the servo from 0 to 180 degrees
        for angle in range(0, 181, 10):  # 0 to 180 in steps of 10
            print(f"Setting angle to {angle} degrees")
            set_angle(angle)
            time.sleep(1)  # Wait for the servo to stabilize
        # Sweep back from 180 to 0 degrees
        for angle in range(180, -1, -10):  # 180 to 0 in steps of 10
            print(f"Setting angle to {angle} degrees")
            set_angle(angle)
            time.sleep(1)  # Wait for the servo to stabilize

except KeyboardInterrupt:
    print("Program stopped by user")

# Stop PWM and clean up the GPIO setup
pwm.stop()
GPIO.cleanup()
