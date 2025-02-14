import RPi.GPIO as GPIO
import time

# Set up GPIO
GPIO.setmode(GPIO.BCM)
servo_pin = 18
GPIO.setup(servo_pin, GPIO.OUT)

# Start PWM at 50Hz (20ms period)
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(0)

# Duty cycles
angle_duty_map = {
    0: 4.4,   # Left
    90: 7.2,  # Middle
    180: 10   # ight
}

def set_servo_angle(angle, step=0.5):
    """
    Move the servo gradually to a specific angle.
    """
    target_duty = angle_duty_map.get(angle, 7.5)  # Default to mid if angle isn't found
    pwm.ChangeDutyCycle(target_duty)
    time.sleep(0.5)  # Hold position

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
