import RPi.GPIO as GPIO
import time
import spidev
from RPLCD.i2c import CharLCD
from threading import Lock, Thread

# Rotary encoder pins
CLK = 23
DT = 24
SW = 25

# LCD setup
lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2)
lcd_lock = Lock()

# Stepper and Servo Pins
STEP_PIN = 17
DIR_PIN = 27
EN_PIN = 22
SERVO_PIN = 18

# Stepper Constants
STEPS_PER_NUMBER = 20
FULL_ROTATION = 800
DELAY_US = 0.0003

# Servo Constants
MOVE_ANGLE = 180
HOLD_DURATION = 2.0
POSITION_THRESHOLD = 160
START_POSITION = 90
angle_duty_map = {0: 4.4, 90: 7.2, 180: 10}
lock_latch = 0

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup([CLK, DT, SW], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup([STEP_PIN, DIR_PIN, EN_PIN], GPIO.OUT)
GPIO.output(EN_PIN, GPIO.LOW)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

# SPI Setup
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

# State Variables
combination = [0, 0, 0]
position = 0
input_active = True
clk_last = GPIO.input(CLK)
last_display = ""
current_position = 0

### --- LCD Functions --- ###
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

    new_line = f"Combo: {display[0]}-{display[1]}-{display[2]}"
    if new_line != last_display:
        with lcd_lock:
            lcd.cursor_pos = (0, 0)
            lcd.write_string("Input Starting   ")
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

def button_monitor():
    global position, input_active

    while True:
        while GPIO.input(SW) == GPIO.HIGH:
            time.sleep(0.01)
        press_time = time.time()
        handled = False

        while GPIO.input(SW) == GPIO.LOW:
            held_duration = time.time() - press_time
            if held_duration >= 1.5 and not handled and input_active:
                position = max(0, position - 1)
                draw_combo(blink=True)
                handled = True
            time.sleep(0.01)

        if not input_active:
            continue

        if time.time() - press_time < 1.5 and not handled:
            if position < 2:
                position += 1
                draw_combo(blink=False)
            else:
                input_active = False
                with lcd_lock:
                    lcd.clear()
                    lcd.write_string("Final Code:")
                    lcd.cursor_pos = (1, 0)
                    lcd.write_string(f"{combination[0]:02}-{combination[1]:02}-{combination[2]:02}")
                print(f"Confirmed: {combination}")
                time.sleep(1)
                unlock_sequence(combination[0], combination[1], combination[2])
                break

        while GPIO.input(SW) == GPIO.LOW:
            time.sleep(0.01)

### --- Stepper & Servo Functions --- ###
def set_servo_angle(angle):
    pwm.ChangeDutyCycle(angle_duty_map.get(angle, 0))
    time.sleep(1)
    pwm.ChangeDutyCycle(0)

def read_mcp3008(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def get_servo_position():
    adc_value = read_mcp3008(0)
    position = (adc_value / 1023) * 180
    scaled = (position - 10) * 1.32
    return round(max(0, min(180, scaled)), 1)

def try_open_shackle():
    print("Attempting to Open Shackle...")
    set_servo_angle(MOVE_ANGLE)
    time.sleep(HOLD_DURATION)
    current_pos = get_servo_position()
    print("Servo Pos:", current_pos)
    if current_pos > POSITION_THRESHOLD:
        print("LOCK OPEN")
        set_servo_angle(START_POSITION)
        return True
    print("LOCK CLOSED")
    set_servo_angle(START_POSITION)
    return False

def step_motor(direction, steps):
    global current_position
    GPIO.output(DIR_PIN, direction)
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(DELAY_US)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(DELAY_US)
    current_position = (current_position + steps if direction == GPIO.HIGH else current_position - steps) % FULL_ROTATION

def dial_combination(first, second, third):
    global current_position
    steps_to_first = (3 * FULL_ROTATION) - (first * STEPS_PER_NUMBER) + current_position
    print(f"Step 1: CW to {first}")
    step_motor(GPIO.LOW, steps_to_first)
    time.sleep(1)

    steps_to_second = ((FULL_ROTATION - (current_position - second * STEPS_PER_NUMBER)) % FULL_ROTATION) + FULL_ROTATION
    print(f"Step 2: CCW to {second}")
    step_motor(GPIO.HIGH, steps_to_second)
    time.sleep(1)

    steps_to_third = (current_position - (third * STEPS_PER_NUMBER)) % FULL_ROTATION
    print(f"Step 3: CW to {third}")
    step_motor(GPIO.LOW, steps_to_third)
    time.sleep(0.5)

    return try_open_shackle()

def increment_combination(first, second, third):
    third += 1
    if third > 39:
        third = 0
        second += 1
        if second > 39:
            second = 0
            first += 1
            if first > 39:
                return None
    return (first, second, third)

def unlock_sequence(first, second, third):
    global pwm, input_active, position

    current_combo = (first, second, third)

    while current_combo:
        f, s, t = current_combo
        combo_str = f"{f:02}-{s:02}-{t:02}"
        print(f"Trying combo: {combo_str}")

        with lcd_lock:
            lcd.cursor_pos = (0, 0)
            lcd.write_string("Trying Combo...  ")
            lcd.cursor_pos = (1, 0)
            lcd.write_string(" " * 16)
            lcd.cursor_pos = (1, 0)
            lcd.write_string(combo_str)

        if dial_combination(f, s, t):
            with lcd_lock:
                lcd.clear()
                lcd.cursor_pos = (0, 0)
                lcd.write_string("Lock OPEN!       ")
                lcd.cursor_pos = (1, 0)
                lcd.write_string(combo_str)
            time.sleep(3)
            cleanup_and_exit()
            return

        current_combo = increment_combination(f, s, t)

    with lcd_lock:
        lcd.clear()
        lcd.cursor_pos = (0, 0)
        lcd.write_string("All Combinations ")
        lcd.cursor_pos = (1, 0)
        lcd.write_string("FAILED!          ")
    time.sleep(3)
    cleanup_and_exit()

def cleanup_and_exit():
    try:
        if pwm:
            pwm.stop()
    except Exception as e:
        print("PWM Stop Error:", e)
    GPIO.cleanup()
    spi.close()
    lcd.clear()
    exit(0)

### --- START --- ###
with lcd_lock:
    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Input Starting   ")
    lcd.cursor_pos = (1, 0)
    lcd.write_string("Combo: 00-00-00  ")

Thread(target=button_monitor, daemon=True).start()
draw_combo(blink=False)

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
    cleanup_and_exit()
