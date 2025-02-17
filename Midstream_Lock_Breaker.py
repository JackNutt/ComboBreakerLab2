import RPi.GPIO as GPIO
import time

# Stepper Motor Configuration
STEP_PIN = 5
DIR_PIN = 2
EN_PIN = 8
STEPS_PER_NUMBER = 20  # Each number = 20 steps
FULL_ROTATION = 800  # 40 numbers * 20 steps
DELAY_US = 0.002  # Reduced delay for faster rotation

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(EN_PIN, GPIO.OUT)
GPIO.output(EN_PIN, GPIO.LOW)  # Enable motor

current_position = 0  # Track dial position

# Stepper Motor Movement Function
def step_motor(direction, steps):
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

# Function to Dial a Combination (Corrected for Lock Mechanics)
def dial_combination(first, second, third):
    global current_position

    # Step 1: Rotate CW at least 2 full rotations to reset the lock, then stop at the first number
    print(f"Turning CW 2 full rotations + stopping at {first}")
    step_motor(GPIO.HIGH, (2 * FULL_ROTATION) + (first * STEPS_PER_NUMBER) - current_position)
    time.sleep(0.5)

    # Step 2: Rotate CCW 1 full rotation past the first number, then stop at the second number
    print(f"Turning CCW past {first}, stopping at {second}")
    step_motor(GPIO.LOW, FULL_ROTATION + ((second * STEPS_PER_NUMBER) - current_position) % FULL_ROTATION)
    time.sleep(0.5)

    # Step 3: Rotate CW directly to the third number
    print(f"Turning CW directly to {third}")
    step_motor(GPIO.HIGH, (third * STEPS_PER_NUMBER) - current_position)
    time.sleep(0.5)

    # Delay to simulate unlocking process
    time.sleep(1)

# Get Starting Combination from User
start_first = int(input("Enter starting first number (0-40): "))
start_second = int(input("Enter starting second number (0-40): "))
start_third = int(input("Enter starting third number (0-40): "))

# Ensure values are within range
start_first %= 41
start_second %= 41
start_third %= 41

# Perform the initial reset spin before brute force starts
print("Performing initial reset spin (Counterclockwise)...")
step_motor(GPIO.LOW, 2 * FULL_ROTATION)  # Counterclockwise reset
time.sleep(0.5)

# Start brute-force attack from the given combination
try:
    for first in range(start_first, 41):  # Start from user input
        for second in range(start_second if first == start_first else 0, 41):
            for third in range(start_third if first == start_first and second == start_second else 0, 41):
                print(f"Trying combination: {first}-{second}-{third}")
                dial_combination(first, second, third)

                # Check if the lock opened (manually or via a sensor)
                time.sleep(0.5)  # Adjust delay if needed

except KeyboardInterrupt:
    print("Interrupted. Cleaning up GPIO...")
finally:
    GPIO.cleanup()
