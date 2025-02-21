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

# Setup SPI for MCP3008
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0 (CS0)
spi.max_speed_hz = 1350000

# Adjustable Parameters
MOVE_ANGLE = 180  # Angle to move the servo to bump the shackle
HOLD_DURATION = 1.0  # Duration to hold the shackle in "open" position
POSITION_THRESHOLD = 160  # Position above which the lock is considered "open"
START_POSITION = 0  # Starting position before each attempt

# Latch Variable (0 = Lock Closed, 1 = Lock Open)
lock_latch = 0

# Duty cycles for servo angles (Adjust these if needed)
angle_duty_map = {
    0: 4.4,   # Left
    90: 7.2,  # Center
    180: 10   # Right
}

# Function to set servo angle
def set_servo_angle(angle):
    """
    Move the servo to a specific angle.
    """
    target_duty = angle_duty_map.get(angle, 7.2)  # Default to center if angle isn't found
    pwm.ChangeDutyCycle(target_duty)
    time.sleep(0.5)  # Allow servo to reach position
    pwm.ChangeDutyCycle(0)  # Stop sending PWM to avoid jitter

# Function to read MCP3008
def read_mcp3008(channel):
    """
    Read ADC value from MCP3008 on a given channel (0-7)
    """
    if channel < 0 or channel > 7:
        return -1
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# Function to get servo position using feedback
def get_servo_position():
    """
    Get servo position from ADC feedback
    Applies offset and scaling for accurate position
    """
    adc_value = read_mcp3008(0)  # Read from CH0
    position = (adc_value / 1023) * 180
    adjusted_position = (position - 10) * 1.157
    adjusted_position = max(0, min(180, adjusted_position))
    return round(adjusted_position, 1)

# Function to try opening the lock
def try_open_shackle():
    """
    Attempt to open the shackle by moving the servo.
    Checks if the lock opens by reading feedback position.
    """
    global lock_latch
    print("\nAttempting to Open Shackle...")
    
    # Move to bump the shackle
    set_servo_angle(MOVE_ANGLE)
    time.sleep(HOLD_DURATION)
    
    # Read the position
    current_position = get_servo_position()
    print("Current Position:", current_position, "°")
    
    # Check if lock is open
    if current_position > POSITION_THRESHOLD:
        print("Lock is OPEN! Ending Program...")
        lock_latch = 1  # Set latch to indicate lock is open
    else:
        print("Lock is STILL CLOSED.")
        # Return to start position
        set_servo_angle(START_POSITION)
        time.sleep(1)
        
        # Verify return position
        final_position = get_servo_position()
        print("Final Position (After Reset):", final_position, "°")
        print("----------")
        
        # Wait for user input to retry (Later to be automated)
        input("Press Enter to try again...")

try:
    print("Starting Lock Opening Routine...")
    
    # Initialize at start position
    set_servo_angle(START_POSITION)
    time.sleep(2)
    
    # Repeat until lock is open
    while lock_latch == 0:
        try_open_shackle()

except KeyboardInterrupt:
    print("Stopping Lock Attempts...")
    pwm.stop()
    GPIO.cleanup()
    spi.close()
