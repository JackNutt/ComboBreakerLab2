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
spi.open(0, 0)  			# Bus 0, Device 0 (CS0)
spi.max_speed_hz = 1350000

# Parameters
MOVE_ANGLE = 180  			# Angle to Bump Shackle
HOLD_DURATION = 1.0  		# Duration to try to open Shackle
POSITION_THRESHOLD = 160  	# Position Where lock is considered "open"
START_POSITION = 90 		# Starting position before each attempt

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
    target_duty = angle_duty_map.get(angle, 0) 	# Default to 0 if angle isn't found
    pwm.ChangeDutyCycle(target_duty)
    time.sleep(0.5)  							# Allow servo to reach position
    pwm.ChangeDutyCycle(0)  					# Stop sending PWM to avoid jitter

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
    adc_value = read_mcp3008(0)
    position = (adc_value/1023)*180
    # So Position is accurate to us
    scaled_position = (position - 10) * 1.32
    scaled_position = max(0, min(180, scaled_position))
    return round(scaled_position, 1)

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
        set_servo_angle(START_POSITION)
        lock_latch = 1  # Set latch to indicate lock is open
    else:
        print("Lock is STILL CLOSED.")
        # Return to start position
        set_servo_angle(START_POSITION)
        time.sleep(3)
        
        # Verify Return Position
        final_position = get_servo_position()
        print("Final Position (After Reset):", final_position, "°")
        print("----------")
        
        # User Input to Retry (AUTOMATE)
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
