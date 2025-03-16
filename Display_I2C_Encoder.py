import time
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD

# Rotary Encoder Pins
CLK = 17
DT = 27
SW = 22

# Initialize LCD (I2C address: 0x27)
lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2)

# Lock combination
combination = [0, 0, 0]  
position = 0  # Tracks current digit being set (0, 1, or 2)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

clk_last = GPIO.input(CLK)

# Function to update LCD display
def update_display():
    lcd.clear()
    lcd.write_string(f"Set Code: {combination[0]:02}-{combination[1]:02}-{combination[2]:02}\n")
    lcd.write_string(f"Digit: {position+1}")

# Function to handle rotary encoder rotation
def rotary_callback(channel):
    global combination, position, clk_last
    clk_state = GPIO.input(CLK)
    dt_state = GPIO.input(DT)

    if clk_state != clk_last:  # Detect rotation
        if dt_state != clk_state:  # Clockwise rotation
            combination[position] = (combination[position] + 1) % 40
        else:  # Counterclockwise rotation
            combination[position] = (combination[position] - 1) % 40

        update_display()  # Update LCD with new value

    clk_last = clk_state

# Function to handle button press (move to next digit)
def button_callback(channel):
    global position
    if position < 2:
        position += 1  # Move to next number
    else:
        lcd.clear()
        lcd.write_string(f"Final Code:\n{combination[0]:02}-{combination[1]:02}-{combination[2]:02}")
        time.sleep(2)  # Show final code
        update_display()  # Reset to editing mode

# Attach event detection
GPIO.add_event_detect(CLK, GPIO.BOTH, callback=rotary_callback, bouncetime=50)
GPIO.add_event_detect(SW, GPIO.FALLING, callback=button_callback, bouncetime=300)

# Initial Display
update_display()

# Keep script running
try:
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
    lcd.clear()
