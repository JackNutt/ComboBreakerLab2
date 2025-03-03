import RPi.GPIO as GPIO
import spidev
import time

# Stepper Motor Configuration
STEP_PIN = 17
DIR_PIN = 27
EN_PIN = 22
STEPS_PER_NUMBER = 20  # Each number = 20 steps
FULL_ROTATION = 800  # 40 numbers * 20 steps
DELAY_US = 0.0005  # Reduced delay for faster rotation

# Servo Configuration
SERVO_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Start PWM at 50Hz (20ms period)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

# Setup SPI for MCP3008 (For Servo Feedback)
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0 (CS0)
spi.max_speed_hz = 1350000

# Servo Parameters
MOVE_ANGLE = 180  # Angle to Bump Shackle
HOLD_DURATION = 1.0  # Duration to try to open Shackle
POSITION_THRESHOLD = 160  # Position where lock is considered "open"
START_POSITION = 90  # Reset position before each attempt

# Duty cycles for servo angles
angle_duty_map = {
    0: 4.4,   # Left
    90: 7.2,  # Center
    180: 10   # Right
}

# Lock status (0 = Lock Closed, 1 = Lock Open)
lock_latch = 0

# Setup GPIO for Stepper Motor
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(EN_PIN, GPIO.OUT)
GPIO.output(EN_PIN, GPIO.LOW)  # Enable motor

current_position = 0  # Track dial position


### --- SERVO FUNCTIONS --- ###

def set_servo_angle(angle):
    """
    Move the servo to a specific angle.
    """
    target_duty = angle_duty_map.get(angle, 0)  # Default to 0 if angle isn't found
    pwm.ChangeDutyCycle(target_duty)
    time.sleep(1)  # Allow servo to reach position
    pwm.ChangeDutyCycle(0)  # Stop sending PWM to avoid jitter

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
    Get servo position from ADC feedback.
    """
    adc_value = read_mcp3008(0)
    position = (adc_value / 1023) * 180
    scaled_position = (position - 10) * 1.32
    scaled_position = max(0, min(180, scaled_position))  # Keep within range
    return round(scaled_position, 1)

def try_open_shackle():
    """
    Attempt to open the lock using the servo.
    """
    global lock_latch
    print("\nAttempting to Open Shackle...")

    # Move servo to bump shackle
    set_servo_angle(MOVE_ANGLE)
    time.sleep(HOLD_DURATION)

    # Read the position
    current_position = get_servo_position()
    print("Current Servo Position:", current_position, "°")

    # Check if lock is open
    if current_position > POSITION_THRESHOLD:
        print("Lock is OPEN! Ending Program...")
        set_servo_angle(START_POSITION)
        time.sleep(1)
        lock_latch = 1  # Lock is open, stop brute force
        return True
    else:
        print("Lock is STILL CLOSED.")

    # Reset Servo to Start Position
    set_servo_angle(START_POSITION)
    time.sleep(1)
    return False


### --- STEPPER FUNCTIONS --- ###

def step_motor(direction, steps):
    """
    Move the stepper motor in a specified direction for a given number of steps.
    """
    global current_position
    GPIO.output(DIR_PIN, direction)
    
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(DELAY_US)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(DELAY_US)

    # Update position
    if direction == GPIO.HIGH:
        current_position += steps
    else:
        current_position -= steps
    current_position %= FULL_ROTATION  # Keep within range

def dial_combination(first, second, third):
    """
    Dial the combination on the rotary lock.
    """
    global current_position

    # Step 1: Rotate CW to reset and reach first number
    steps_to_first = (2 * FULL_ROTATION) + (first * STEPS_PER_NUMBER) - current_position
    print(f"Turning CW 2 full rotations + stopping at {first}")
    step_motor(GPIO.HIGH, steps_to_first)
    time.sleep(1)

    # Step 2: Rotate CCW past first number, stopping at second number
    steps_to_second = ((FULL_ROTATION + (current_position - second * STEPS_PER_NUMBER)) % FULL_ROTATION) + FULL_ROTATION
    if steps_to_second < STEPS_PER_NUMBER:
        steps_to_second += FULL_ROTATION
    print(f"Turning CCW past {first}, stopping at {second}")
    step_motor(GPIO.LOW, steps_to_second)
    time.sleep(1)

    # Step 3: Rotate CW directly to the third number
    steps_to_third = ((third * STEPS_PER_NUMBER) - current_position) % FULL_ROTATION
    if steps_to_third < 0:
        steps_to_third += FULL_ROTATION
    print(f"Turning CW directly to {third}")
    step_motor(GPIO.HIGH, steps_to_third)
    time.sleep(0.5)

    # Attempt to open the lock
    if try_open_shackle():
        return True  # Stop brute force if lock is open

    return False  # Continue brute force


def increment_combination(first, second, third):
    """
    Increment the combination in ascending order.
    """
    third += 1
    if third > 39:
        third = 0
        second += 1
        if second > 39:
            second = 0
            first += 1
            if first > 39:
                return None  # End brute-force
    return (first, second, third)


### --- MAIN PROGRAM --- ###

try:
    # Get Starting Combination from User
    print("Enter the starting combination:")
    start_first = int(input("First number (0-39): "))
    start_second = int(input("Second number (0-39): "))
    start_third = int(input("Third number (0-39): "))

    # Validate Input
    if not (0 <= start_first <= 39) or not (0 <= start_second <= 39) or not (0 <= start_third <= 39):
        raise ValueError("Invalid combination numbers. Must be between 0 and 39.")

    current_combination = (start_first, start_second, start_third)

    while current_combination:
        first, second, third = current_combination
        print(f"Trying combination: {first}-{second}-{third}")
        if dial_combination(first, second, third):
            break  # Stop if lock opens

        current_combination = increment_combination(first, second, third)

except KeyboardInterrupt:
    print("Interrupted. Cleaning up GPIO...")
finally:
    pwm.stop()
    GPIO.cleanup()
    spi.close()
