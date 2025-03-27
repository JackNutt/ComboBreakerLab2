import RPi.GPIO as GPIO
import time

# Rotary encoder GPIO pins
CLK = 17   # Clock
DT = 27    # Data
SW = 22    # Push button

# Lock combination input
combination = [0, 0, 0]
position = 0  # Which digit you're editing (0, 1, or 2)

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize last state
clk_last = GPIO.input(CLK)

def rotary_check():
    global clk_last, combination, position

    clk_current = GPIO.input(CLK)
    dt_current = GPIO.input(DT)

    if clk_current != clk_last:
        if dt_current != clk_current:
            # Clockwise
            combination[position] = (combination[position] + 1) % 40
        else:
            # Counter-clockwise
            combination[position] = (combination[position] - 1) % 40

        print(f"Input Starting Code: {combination[0]:02}-{combination[1]:02}-{combination[2]:02}")

    clk_last = clk_current

def button_callback(channel):
    global position
    if position < 2:
        position += 1
        print(f"Moving to Digit {position + 1}")
    else:
        print(f"Final Code Entered: {combination[0]:02}-{combination[1]:02}-{combination[2]:02}")
        # Trigger the next step

# Event for pushbutton
GPIO.add_event_detect(SW, GPIO.FALLING, callback=button_callback, bouncetime=300)

try:
    while True:
        rotary_check()
        time.sleep(0.005)

except KeyboardInterrupt:
    GPIO.cleanup()
