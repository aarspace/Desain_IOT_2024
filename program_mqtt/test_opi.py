import OPi.GPIO as GPIO

GPIO.setmode(GPIO.SUNXI)
GPIO.setup("PC11", GPIO.IN)

# Define a callback function for the interrupt
def callback(channel):
    print("Interrupt detected on GPIO", channel)

# Add event detection for rising edge
GPIO.add_event_detect("PC11", GPIO.RISING, callback=callback)

# Keep the program running to catch the interrupt
try:
    while True:
        pass
except KeyboardInterrupt:
    GPIO.cleanup()
