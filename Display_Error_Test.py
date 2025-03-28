import RPi.GPIO as GPIO
import time
from RPLCD.i2c import CharLCD
from threading import Lock, Thread

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
lcd_lock = Lock()
last_display = ""

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

clk_last = GPIO.input(CLK)

# Initial message
with lcd_lock:
    lcd.clear()
    time.sleep(0.05)
    lcd.write_string("Input Starting")

def draw_combo(blink=False):
    global last_display
    display = []

    for i in range(3):
        if not input_active:
            display.append(f"{combination[i]:02}")
        elif i == position:
            display.append(f"{combination[i]:02}")
        else:
            display.append("  " if blink else f"{combination[i]:02}")

    new_line = f"Combo {display[0]}-{display[1]}-{display[2]}"
    if new_line != last_display:
        with lcd_lock:
            lcd.cursor_pos = (1, 0)
            lcd.write_string(" " * 16)
            lcd.cursor_pos = (1, 0)
            lcd.write_string(new_line)
        last_display = new_line

def rotary_check():
    global clk_last, combination, position

    if not input_active:
        return

    clk_current = GPIO.input(CLK)

    if clk_last == 1 and clk_current == 0:
        dt_current = GPIO.input(DT)

        if dt_current == 1:
            combination[position] = (combination[position] + 1) % 40
        else:
            combination[position] = (combination[position] - 1) % 40

        draw_combo(blink=False)
        time.sleep(0.05)

    clk_last = clk_current

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
        with lcd_lock:
            lcd.clear()
            time.sleep(0.05)
            lcd.write_string("Final Code:")
            lcd.cursor_pos = (1, 0)
            lcd.write_string(f"{combination[0]:02}-{combination[1]:02}-{combination[2]:02}")
        print(f"Final Code Entered: {combination[0]:02}-{combination[1]:02}-{combination[2]:02}")

def long_press_monitor():
    while True:
        # Wait for button to be pressed
        while GPIO.input(SW) == GPIO.HIGH:
            time.sleep(0.01)

        press_time = time.time()

        # Wait while held down
        while GPIO.input(SW) == GPIO.LOW:
            time.sleep(0.01)

        duration = time.time() - press_time

        if duration >= 3 and input_active:
            global position
            if position == 2:
                position = 1
                draw_combo(blink=False)
                print("Long press: Reverted to Digit 2")
            elif position == 1:
                position = 0
                draw_combo(blink=False)
                print("Long press: Reverted to Digit 1")

# Attach short press detector
GPIO.add_event_detect(SW, GPIO.FALLING, callback=button_callback, bouncetime=300)

# Start background thread for long press detection
Thread(target=long_press_monitor, daemon=True).start()

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

        time.sleep(0.001)

except KeyboardInterrupt:
    GPIO.cleanup()
    with lcd_lock:
        lcd.clear()
