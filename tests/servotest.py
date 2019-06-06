#!/usr/bin/env python3

# Exercises the servo

from time import sleep
import RPi.GPIO as GPIO

I2C_BUS = 1
SERVO_PIN = 19

def release_ball():
    CLOSED = 4.5
    OPEN = 10
    SERVO_FREQUENCY = 50  # 50 Hz
    pwm = GPIO.PWM(SERVO_PIN, SERVO_FREQUENCY)
    pwm.start(7.5)
    
    pwm.ChangeDutyCycle(CLOSED)  # 0 degrees
    sleep(1)
    pwm.ChangeDutyCycle(OPEN) # 180 degrees
    sleep(1)
    pwm.ChangeDutyCycle(CLOSED)  # 0 degrees

if __name__ == '__main__':
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    release_ball()
