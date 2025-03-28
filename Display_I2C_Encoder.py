import RPi.GPIO as GPIO
import time
from RPLCD.i2c import CharLCD

# Rotary encoder GPIO pins
CLK = 23
DT = 24
SW = 25

# Lock combination input
combination = [0, 0, 0]
position = 0  # 0 = first digit, 1 = second, 2 = third
input_active = True  # Flag to control input/blinking state

# LCD setup
lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2)

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

clk_last = GPIO.input(CLK)

# Initial message
lcd.clear()
lcd.write_string("Input Starting")
time.sleep(0.1)

def draw_combo(blink=False):
    lcd.cursor_pos = (1, 0)
    display = []

    for i in range(3):
        if not input_active:
            display.append(f"{combination[i]:02}")
        elif i == position:
            display.append(f"{combination[i]:02}")
        else:
            display.append("  " if blink else f"{combination[i]:02}")

    lcd_line = f"Combo {display[0]}-{display[1]}-{display[2]}"
    lcd.write_string(lcd_line.ljust(16))  # Pad to clear old chars

ROTARY_STATES = {
    (0b00, 0b01): +1,
    (0b01, 0b11): +1,
    (0b11, 0b10): +1,
    (0b10, 0b00): +1,
    (0b00, 0b10): -1,
    (0b10, 0b11): -1,
    (0b11, 0b01): -1,
    (0b01, 0b00): -1,
}

# Initialize previous encoder state
prev_state = (GPIO.input(CLK) << 1) | GPIO.input(DT)

def rotary_check():
    global prev_state, combination, position

    if not input_active:
        return

    # Read current encoder state
    clk = GPIO.input(CLK)
    dt = GPIO.input(DT)
    curr_state = (clk << 1) | dt

    if prev_state != curr_state:
        step = ROTARY_STATES.get((prev_state, curr_state), 0)
        if step != 0:
            combination[position] = (combination[position] + step) % 40
            draw_combo(blink=False)
            time.sleep(0.05)  # debounce delay for stability

        prev_state = curr_state

def button_callback(channel):
    global position, input_active

    if not input_active:
        return

    if position < 2:
        position += 1
        draw_combo(blink=False)
        print(f"Moving to Digit {position + 1}")
    else:
        input_active = False

        time.sleep(0.05)
        lcd.clear()
        time.sleep(0.1)

        lcd.write_string("Final Code:")
        lcd.cursor_pos = (1, 0)
        final_code = f"{combination[0]:02}-{combination[1]:02}-{combination[2]:02}"
        lcd.write_string(final_code.ljust(16))
        print(f"Final Code Entered: {final_code}")

GPIO.add_event_detect(SW, GPIO.FALLING, callback=button_callback, bouncetime=300)

# Start with initial combo line
draw_combo(blink=False)

# Main loop
try:
    blink_state = False
    blink_timer = time.time()

    while True:
        rotary_check()

        if input_active and (time.time() - blink_timer > 0.5):
            blink_state = not blink_state
            draw_combo(blink=blink_state)
            blink_timer = time.time()

        time.sleep(0.01)  # small delay to avoid CPU hammering

except KeyboardInterrupt:
    GPIO.cleanup()
    lcd.clear()
