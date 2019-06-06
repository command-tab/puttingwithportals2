#!/usr/bin/env python3

from qwiic import Relay, MP3Trigger
from time import sleep
import RPi.GPIO as GPIO
import asyncio
import sys

# Qwiic I2C device constants
I2C_BUS = 1
LAUNCH_RELAY_ADDRESS = 0x18
MP3_TRIGGER_ADDRESS = 0x37

# GPIO pin constants use BCM numbering.
# Sparkfun Pi Wedge prefixes BCM numbering with 'G'.
PUTT_SENSOR_PIN = 18
CUP_SENSOR_PIN = 20

RF_RX_A_PIN = 21
RF_RX_B_PIN = 22
RF_RX_C_PIN = 23
RF_RX_D_PIN = 24

SERVO_PIN = 19

# I2C devices
launch_relay = Relay(I2C_BUS, LAUNCH_RELAY_ADDRESS)
sfx_mp3_trigger = MP3Trigger(I2C_BUS, MP3_TRIGGER_ADDRESS)

# Global game state
playing = False

def release_ball():
    """
    Releases exactly on golf ball from the queue using a servo
    with two piano wire obstructors inserted into a pipe. When one
    obstructor moves out of the way to let the balls roll, the other
    blocks them all one ball away, so the whole queue only advances by one.
    No longer obstructed, the end ball is released and rolls away.
    """
    SERVO_FREQUENCY = 50  # 50 Hz
    OBSTRUCTOR_CLOSED_DUTY_CYCLE = 4.5
    OBSTRUCTOR_OPEN_DUTY_CYCLE = 10
    pwm = GPIO.PWM(SERVO_PIN, SERVO_FREQUENCY)
    pwm.start(7.5)
    pwm.ChangeDutyCycle(OBSTRUCTOR_CLOSED_DUTY_CYCLE)
    sleep(1)
    pwm.ChangeDutyCycle(OBSTRUCTOR_OPEN_DUTY_CYCLE)
    sleep(1)
    pwm.ChangeDutyCycle(OBSTRUCTOR_CLOSED_DUTY_CYCLE)

def launch():
    print('Launching')
    launch_relay.on()
    release_ball()
    launch_relay.off()

def handle_putt(pin):
    global playing
    if not playing:
        print('Detected putt')
        playing = True
        launch()

def handle_cup(pin):
    global playing
    if playing:
        print('Detected cup sink')
        sfx_mp3_trigger.play_track(0x04)
    playing = False

def handle_sfx_a(pin):
    print('Playing SFX A')
    sfx_mp3_trigger.play_track(0x02)

def handle_sfx_b(pin):
    print('Playing SFX B')
    sfx_mp3_trigger.play_track(0x03)

def handle_sfx_c(pin):
    print('Playing SFX C')
    sfx_mp3_trigger.play_track(0x04)

def handle_sfx_d(pin):
    print('Playing SFX D')
    sfx_mp3_trigger.play_track(0x05)


if __name__ == '__main__':
    try:
        # SFX
        print('Powerup initiated')
        sfx_mp3_trigger.set_volume(0x01)
        sfx_mp3_trigger.play_track(0x01)
        sleep(2)

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        # Configure GPIO pin modes for each connected device type
        print('Configuring pins')
        for pin in [PUTT_SENSOR_PIN, CUP_SENSOR_PIN]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Default high
        for pin in [RF_RX_A_PIN, RF_RX_B_PIN, RF_RX_C_PIN, RF_RX_D_PIN]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Default low
        GPIO.setup(SERVO_PIN, GPIO.OUT)

        # Add interrupts
        # IR bream-break sensors are default high when the beam is unbroken, and go low when broken.
        # RF module pins go high for as long as the keyfob button is held.
        print('Adding interrupts')
        
        GPIO.add_event_detect(PUTT_SENSOR_PIN, GPIO.FALLING, callback=handle_putt, bouncetime=100)
        GPIO.add_event_detect(CUP_SENSOR_PIN, GPIO.FALLING, callback=handle_cup, bouncetime=100)
        
        GPIO.add_event_detect(RF_RX_A_PIN, GPIO.RISING, callback=handle_sfx_a, bouncetime=500)
        GPIO.add_event_detect(RF_RX_B_PIN, GPIO.RISING, callback=handle_sfx_b, bouncetime=500)
        GPIO.add_event_detect(RF_RX_C_PIN, GPIO.RISING, callback=handle_sfx_c, bouncetime=500)
        GPIO.add_event_detect(RF_RX_D_PIN, GPIO.RISING, callback=handle_sfx_d, bouncetime=500)

        # SFX
        print('Powerup complete')
        sfx_mp3_trigger.play_track(0x02)
        sleep(2)

        # Run the event loop
        loop = asyncio.get_event_loop()
        print('Awaiting putt')
        loop.run_forever()
        loop.close()
    except KeyboardInterrupt:
        sys.exit()
