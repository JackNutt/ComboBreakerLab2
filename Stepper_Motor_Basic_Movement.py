# Libraries
import RPi.GPIO as GPIO
import time

# Pins
STEP_PIN = 5
DIR_PIN = 2
EN_PIN = 8

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(EN_PIN, GPIO.OUT)

# Enable Motor
GPIO.output(EN_PIN, GPIO.LOW) 

# Movement of the Motor
def step_motor(direction, steps=800, delay_us=0.005):
    GPIO.output(DIR_PIN, direction)
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(delay_us)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(delay_us)

# Moving the Motor in Each Direction
try:
    while True:
        step_motor(GPIO.HIGH)  # Move forward
        time.sleep(1)  # Pause
        step_motor(GPIO.LOW)   # Move backward
        time.sleep(1)  # Pause

# Stops by Pressing Ctrl+C
except KeyboardInterrupt:
    GPIO.cleanup()  # Cleanup GPIO on exit
