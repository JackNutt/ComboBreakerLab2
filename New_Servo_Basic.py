import RPi.GPIO as GPIO
import time

# Set up GPIO
GPIO.setmode(GPIO.BCM)
servo_pin = 18
GPIO.setup(servo_pin, GPIO.OUT)

# Start PWM at 50Hz (20ms period)
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(0)

# Updated Duty Cycles (corresponding to 0°, 90°, 180° for FS5115M-FB)
angle_duty_map = {
    0: 2.5,     # Full Left (500 µs pulse)
    90: 7.5,    # Center (1500 µs pulse)
    180: 12.5   # Full Right (2500 µs pulse)
}

def set_servo_angle(angle):
    """
    Move the servo directly to a specific angle.
    """
    duty = angle_duty_map.get(angle, 7.5)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)  # Let it settle

try:
    print("Initializing Servo to Middle (90°)...")
    set_servo_angle(90)
    time.sleep(2)

    while True:
        print("Moving to 0° (Left)")
        set_servo_angle(0)
        time.sleep(2)

        print("Moving to 90° (Center)")
        set_servo_angle(90)
        time.sleep(2)

        print("Moving to 180° (Right)")
        set_servo_angle(180)
        time.sleep(2)

except KeyboardInterrupt:
    print("Stopping")
    pwm.stop()
    GPIO.cleanup()
