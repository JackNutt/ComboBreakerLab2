import RPi.GPIO as GPIO
import time
from RPLCD.i2c import CharLCD

# Rotary encoder GPIO pins (updated)
CLK = 23
DT = 24
SW = 25

# Initialize LCD (I2C address: 0x27)
lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2)

# Lock combination input
combination = [0, 0, 0]
position = 0  # 0 = first digit, 1 = second, 2 = third

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

clk_last = GPIO.input(CLK)

def update_display():
    lcd.clear()
    lcd.write_string(f"Code: {combination[0]:02}-{combination[1]:02}-{combination[2]:02}\n")
    lcd.write_string(f"Digit: {position + 1}")

def rotary_check():
    global clk_last, combination, position

    clk_current = GPIO.input(CLK)

    # Only process on falling edge
    if clk_last == 1 and clk_current == 0:
        dt_current = GPIO.input(DT)

        if dt_current == 1:
            combination[position] = (combination[position] + 1) % 40
        else:
            combination[position] = (combination[position] - 1) % 40

        update_display()
        time.sleep(0.05)  # Small debounce/cooldown

    clk_last = clk_current

def button_callback(channel):
    global position
    if position < 2:
        position += 1
        update_display()
        print(f"Moving to Digit {position + 1}")
    else:
        lcd.clear()
        lcd.write_string("Final Code:")
        lcd.cursor_pos = (1, 0)
        lcd.write_string(f"{combination[0]:02}-{combination[1]:02}-{combination[2]:02}")
        print(f"Final Code Entered: {combination[0]:02}-{combination[1]:02}-{combination[2]:02}")
        time.sleep(3)
        position = 0  # Reset to allow re-entry
        update_display()

# Attach button event
GPIO.add_event_detect(SW, GPIO.FALLING, callback=button_callback, bouncetime=300)

# Initial display
update_display()

# Main loop
try:
    while True:
        rotary_check()
        time.sleep(0.001)

except KeyboardInterrupt:
    GPIO.cleanup()
    lcd.clear()
