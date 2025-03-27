import RPi.GPIO as GPIO
import time

# Rotary encoder GPIO pins
CLK = 23
DT = 24
SW = 25

# Combination state
combination = [0, 0, 0]
position = 0

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

clk_last = GPIO.input(CLK)

def rotary_check():
    global clk_last, combination, position

    clk_current = GPIO.input(CLK)

    # Only process on falling edge
    if clk_last == 1 and clk_current == 0:
        dt_current = GPIO.input(DT)

        if dt_current == 1:
            # Clockwise
            combination[position] = (combination[position] + 1) % 40
        else:
            # Counter-clockwise
            combination[position] = (combination[position] - 1) % 40

        print(f"Input Starting Code: {combination[0]:02}-{combination[1]:02}-{combination[2]:02}")
        time.sleep(0.05)  # debounce / cooldown

    clk_last = clk_current

def button_callback(channel):
    global position
    if position < 2:
        position += 1
        print(f"Moving to Digit {position + 1}")
    else:
        print(f"Final Code Entered: {combination[0]:02}-{combination[1]:02}-{combination[2]:02}")

GPIO.add_event_detect(SW, GPIO.FALLING, callback=button_callback, bouncetime=300)

try:
    while True:
        rotary_check()
        time.sleep(0.001)

except KeyboardInterrupt:
    GPIO.cleanup()
