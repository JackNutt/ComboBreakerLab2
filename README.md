# Combo Breaker
Project Lab 2 - Rotary Combination Lock Solver
Project Description
This project utilizes a Raspberry Pi, OpenCV, and Python to systematically attempt to crack a 0-40 rotary combination lock. Given that there are over 64,000 possible combinations, the system automates the process of testing each combination efficiently.

## Files Overview
### Basic_Servo_Movement.py
* Description: Moves a servo through preset positions (0° → 90° → 180° → 0°).
* Purpose: Determines the duty cycles and PWM frequency for the servo motor, specifically the Batan D125F.

### Lock_Breaker.py
* Description: Implements the core logic to systematically rotate the lock through all possible combinations, starting from 0-0-0 and iterating sequentially.
* Purpose: Automates the brute-force solving of the rotary lock.

### Stepper_Motor_Basic_Movement.py
* Description: Rotates a NEMA 17 stepper motor 360° clockwise, then 360° counterclockwise.
* Purpose: Demonstrates the speed and precision of the stepper motor.

## Setup & Requirements
### Hardware:
* Raspberry Pi 5
* Batan D125F Servo Motor
* NEMA 17 Stepper Motor
* Rotary Combination Lock
* EASON Stepper Motor Driver TB6600
### Software Dependencies:
* Python 3.x
* OpenCV
* RPi.GPIO / pigpio
