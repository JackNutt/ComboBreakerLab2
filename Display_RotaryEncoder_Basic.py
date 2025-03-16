import RPi.GPIO as GPIO
import time

# Rotary encoder GPIO pins
CLK = 23   # Clockwise rotation
DT = 24    # Counterclockwise rotation
SW = 25    # Push-button

# Lock combination input (3 digits)
combination = [0, 0, 0]  
position = 0  # Tracks which digit is being set (0, 1, or 2)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

clk_last = GPIO.input(CLK)

def rotary_callback(channel):
    global combination, position, clk_last
    clk_state = GPIO.input(CLK)
    dt_state = GPIO.input(DT)
    
    if clk_state != clk_last:  # Detect rotation change
        if dt_state != clk_state:  # Clockwise rotation
            combination[position] = (combination[position] + 1) % 40  # Increment
        else:  # Counterclockwise rotation
            combination[position] = (combination[position] - 1) % 40  # Decrement
        
        print(f"Input Starting Code: {combination[0]:02}-{combination[1]:02}-{combination[2]:02}")

    clk_last = clk_state

def button_callback(channel):
    global position
    if position < 2:
        position += 1  # Move to next number
        print(f"Moving to Next Digit: {position + 1}")
    else:
        print(f"Final Code Entered: {combination[0]:02}-{combination[1]:02}-{combination[2]:02}")
        # Here, trigger the lock mechanism or start the unlocking process

# Attach event detection
GPIO.add_event_detect(CLK, GPIO.BOTH, callback=rotary_callback, bouncetime=50)
GPIO.add_event_detect(SW, GPIO.FALLING, callback=button_callback, bouncetime=300)

try:
    while True:
        time.sleep(0.1)  # Keep script running

except KeyboardInterrupt:
    GPIO.cleanup()
