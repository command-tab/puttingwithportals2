#!/usr/bin/env python3

from qwiic import Relay, MP3Trigger
from time import sleep
import RPi.GPIO as GPIO

# Qwiic I2C device constants
I2C_BUS = 1
RELAY_ADDRESS = 0x18
MP3_ADDRESS = 0x37

# GPIO pin constants using BCM numbering (Pi Wedge silkscreen in parens)
PUTT_SENSOR_PIN = 18  # (G18)
CUP_SENSOR_PIN = 20  # (G20)
RF_RX_A_PIN = 17  # (G17)
RF_RX_B_PIN = 16  # (G16)
RF_RX_C_PIN = 13  # (G13)
RF_RX_D_PIN = 12  # (G12)
SERVO_PIN = 19  # (G19)

# Start up
launch_relay = Relay(I2C_BUS, RELAY_ADDRESS)
sfx_mp3_trigger = MP3Trigger(I2C_BUS, MP3_ADDRESS)
sfx_mp3_trigger.set_volume(0x03)
sfx_mp3_trigger.play_track(0x01)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Configure GPIO pin modes for each connected device type
for pin in [PUTT_SENSOR_PIN, CUP_SENSOR_PIN]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
for pin in [RF_RX_A_PIN, RF_RX_B_PIN, RF_RX_C_PIN, RF_RX_D_PIN]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Game state
playing = False

def release_ball():
    pwm = GPIO.PWM(SERVO_PIN, 50)
    pwm.start(7.5)
    pwm.ChangeDutyCycle(7.5)  # turn towards 90 degree
    time.sleep(1)
    pwm.ChangeDutyCycle(2.5)  # turn towards 0 degree
    time.sleep(1)
    pwm.ChangeDutyCycle(12.5) # turn towards 180 degree

def launch():
    relay.on()
    release_ball()
    relay.off()

def handle_putt():
    playing = True
    launch()

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
