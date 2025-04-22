import RPi.GPIO as GPIO
import spidev
import time

# Set up GPIO for Servo Control
GPIO.setmode(GPIO.BCM)
servo_pin = 18
GPIO.setup(servo_pin, GPIO.OUT)

# Start PWM at 50Hz (20ms period)
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(0)

# Updated Duty cycles for 0° to 180° using 500–2500 µs pulse range
angle_duty_map = {
    0: 2.5,     # Full Left (500 µs)
    90: 7.5,    # Center (1500 µs)
    180: 12.5   # Full Right (2500 µs)
}

# Setup SPI for MCP3008
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0 (CS0)
spi.max_speed_hz = 1350000

def set_servo_angle(angle):
    """
    Move the servo to a specific angle.
    """
    target_duty = angle_duty_map.get(angle, 7.5)  # Default to center if angle isn't found
    pwm.ChangeDutyCycle(target_duty)
    time.sleep(0.5)  # Allow servo to reach position
    pwm.ChangeDutyCycle(0)  # Stop sending PWM to reduce jitter

def read_mcp3008(channel):
    """
    Read ADC value from MCP3008 on a given channel (0-7)
    """
    if channel < 0 or channel > 7:
        return -1
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def get_servo_position():
    """
    Convert ADC value to a position value (0 to 180 degrees)
    """
    adc_value = read_mcp3008(0)  # Read from CH0
    position = (adc_value / 1023) * 180
    return round(position, 1)

try:
    print("Initializing Servo to Center (90°)...")
    set_servo_angle(90)
    time.sleep(2)

    while True:
        print("Moving to 0° (Left)")
        set_servo_angle(0)
        time.sleep(2)
        print("Servo Position:", get_servo_position(), "°")

        print("Moving to 90° (Center)")
        set_servo_angle(90)
        time.sleep(2)
        print("Servo Position:", get_servo_position(), "°")

        print("Moving to 180° (Right)")
        set_servo_angle(180)
        time.sleep(2)
        print("Servo Position:", get_servo_position(), "°")

except KeyboardInterrupt:
    print("Stopping")
    pwm.stop()
    GPIO.cleanup()
    spi.close()
