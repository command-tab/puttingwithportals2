#!/usr/bin/env python3

from qwiic import Relay, MP3Trigger
from time import sleep
import RPi.GPIO as GPIO

# Qwiic I2C device constants
I2C_BUS = 1
RELAY_ADDRESS = 0x18
MP3_ADDRESS = 0x37

# GPIO pin constants
PUTT_SENSOR_PIN = 1
CUP_SENSOR_PIN = 2
RF_RX_A_PIN = 3
RF_RX_B_PIN = 4
RF_RX_C_PIN = 5
RF_RX_D_PIN = 6
SERVO_PIN = 7

# Start up
launch_relay = Relay(I2C_BUS, RELAY_ADDRESS)
sfx_mp3_trigger = MP3Trigger(I2C_BUS, MP3_ADDRESS)
sfx_mp3_trigger.set_volume(0x03)
sfx_mp3_trigger.play_track(0x01)

GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BOARD)

# Configure GPIO pin modes for each connected device type
for pin in [PUTT_SENSOR_PIN, CUP_SENSOR_PIN]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
for pin in [RF_RX_A_PIN, RF_RX_B_PIN, RF_RX_C_PIN, RF_RX_D_PIN]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Game state
playing = False

def handle_putt():
    playing = True

    pwm = GPIO.PWM(SERVO_PIN, 50)
    pwm.start(7.5)

    relay.on()

    p.ChangeDutyCycle(7.5)  # turn towards 90 degree
    time.sleep(1)
    p.ChangeDutyCycle(2.5)  # turn towards 0 degree
    time.sleep(1)
    p.ChangeDutyCycle(12.5) # turn towards 180 degree

    relay.off()

def handle_cup():
    if playing:
        sfx_mp3_trigger.play_track(0x03)
    playing = False

def handle_sfx_a():
   sfx_mp3_trigger.play_track(0x01)

def handle_sfx_b():
   sfx_mp3_trigger.play_track(0x02)

def handle_sfx_c():
   sfx_mp3_trigger.play_track(0x03)

def handle_sfx_d():
   sfx_mp3_trigger.play_track(0x04)

# Add interrupts
GPIO.add_event_detect(PUTT_SENSOR_PIN, GPIO.RISING, callback=handle_putt, bouncetime=100)
GPIO.add_event_detect(CUP_SENSOR_PIN, GPIO.RISING, callback=handle_cup, bouncetime=100)
GPIO.add_event_detect(RF_RX_A_PIN, GPIO.RISING, callback=handle_sfx_a, bouncetime=100)
GPIO.add_event_detect(RF_RX_B_PIN, GPIO.RISING, callback=handle_sfx_b, bouncetime=100)
GPIO.add_event_detect(RF_RX_C_PIN, GPIO.RISING, callback=handle_sfx_c, bouncetime=100)
GPIO.add_event_detect(RF_RX_D_PIN, GPIO.RISING, callback=handle_sfx_d, bouncetime=100)

# GPIO.cleanup()
