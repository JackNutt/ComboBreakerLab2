import RPi.GPIO as GPIO
import time

# Stepper Motor Configuration
STEP_PIN = 17
DIR_PIN = 27
EN_PIN = 22
STEPS_PER_NUMBER = 20  # Each number = 20 steps
FULL_ROTATION = 800  # 40 numbers * 20 steps
DELAY_US = 0.0005  # Reduced delay for faster rotation

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
    steps_to_first = (2 * FULL_ROTATION) + (first * STEPS_PER_NUMBER) - current_position
    print(f"Turning CW 2 full rotations + stopping at {first}")
    step_motor(GPIO.HIGH, steps_to_first)
    time.sleep(1)

    # Step 2: Rotate CCW 1 full rotation past the first number, then stop at the second number
    steps_to_second = ((FULL_ROTATION + (current_position - second * STEPS_PER_NUMBER)) % FULL_ROTATION) + FULL_ROTATION
    if steps_to_second < STEPS_PER_NUMBER:
        print("Fuckkkkkkkkkkkkkkkkkkkkkkkkkkk")
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
    time.sleep(1)

    # Delay to simulate unlocking process
    time.sleep(2)

# Function to Increment Combination in Ascending Order
def increment_combination(first, second, third):
    third += 1
    if third > 39:
        third = 0
        second += 1
        if second > 39:
            second = 0
            first += 1
            if first > 39:
                return None  # End of all combinations
    return (first, second, third)

# Main Program
try:
    # Get Starting Combination from User
    print("Enter the starting combination:")
    start_first = int(input("First number (0-39): "))
    start_second = int(input("Second number (0-39): "))
    start_third = int(input("Third number (0-39): "))

    # Validate Input
    if not (0 <= start_first <= 39) or not (0 <= start_second <= 39) or not (0 <= start_third <= 39):
        raise ValueError("Invalid combination numbers. Must be between 0 and 39.")

    # Start from User's Combination
    current_combination = (start_first, start_second, start_third)

    # Brute-force attack: Iterate through all combinations starting from the user's input
    while current_combination:
        first, second, third = current_combination
        print(f"Trying combination: {first}-{second}-{third}")
        dial_combination(first, second, third)

        # Check if the lock opened (Integration with servo feedback will be added later)
        time.sleep(0.5)  # Adjust delay if needed

        # Get next combination
        current_combination = increment_combination(first, second, third)

except KeyboardInterrupt:
    print("Interrupted. Cleaning up GPIO...")
finally:
    GPIO.cleanup()
