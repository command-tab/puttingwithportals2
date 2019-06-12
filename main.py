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

# GPIO pin constants (using BCM numbering)
PUTT_SENSOR_PIN = 18
CUP_SENSOR_PIN = 20
RF_RX_A_PIN = 21  # Greetings
RF_RX_B_PIN = 27  # Non sequiturs
RF_RX_C_PIN = 23  # Taunts
RF_RX_D_PIN = 24  # Clear game state (if player picks up ball without tripping cup sensor)
SERVO_PIN = 19

# I2C devices
launch_relay = Relay(I2C_BUS, LAUNCH_RELAY_ADDRESS)
mp3_trigger = MP3Trigger(I2C_BUS, MP3_TRIGGER_ADDRESS)

# Global game state
playing = False

# Last audio tracks played (to avoid playing the same audio again soon)
last_non_sequitur_index = None
last_taunt_index = None
last_congratulation_index = None

audio_greeting = 1  # 1 greeting track
audio_non_sequiturs = list(range(2, 11))  # 9 tracks
audio_taunts = list(range(11, 22))  # 11 tracks
audio_congratulations = list(range(22, 40))  # 18 tracks


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

        # Play next congratulation
        global mp3_trigger
        global last_congratulation_index
        global audio_congratulations

        if last_congratulation_index:
            i = audio_congratulations.index(last_congratulation_index)
            if (i + 1) > len(audio_congratulations):
                # Return to beginning of audio list if we've reached the end
                i = 0
            else:
                # Advance to the next track
                i = i + 1
            track = audio_congratulations[i]
            last_congratulation_index = i
        else:
            track = audio_congratulations[0]
            last_congratulation_index = 0
        print('Playing T{0:03d}.mp3'.format(audio_congratulations[i - 1]))
        mp3_trigger.play_track(track)

    playing = False


def handle_rf_a(pin):
    print('Pressed RF A - Greeting')

    # Play greeting
    global mp3_trigger
    global audio_greeting
    mp3_trigger.play_track(audio_greeting)


def handle_rf_b(pin):
    print('Pressed RF B - Non sequitur')

    # Play next congratulation
    global mp3_trigger
    global last_non_sequitur_index
    global audio_non_sequiturs

    if last_non_sequitur_index:
        i = audio_non_sequiturs.index(last_non_sequitur_index)
        if (i + 1) > len(audio_non_sequiturs):
            # Return to beginning of audio list if we've reached the end
            i = 0
        else:
            # Advance to the next track
            i = i + 1
        track = audio_non_sequiturs[i]
        last_non_sequitur_index = i
    else:
        track = audio_non_sequiturs[0]
        last_non_sequitur_index = 0
    print('Playing T{0:03d}.mp3'.format(audio_non_sequiturs[i - 1]))
    mp3_trigger.play_track(track)


def handle_rf_c(pin):
    print('Pressed RF C - Taunt')

    # Play next congratulation
    global mp3_trigger
    global last_taunt_index
    global audio_taunts

    if last_taunt_index:
        i = audio_taunts.index(last_taunt_index)
        if (i + 1) > len(audio_taunts):
            # Return to beginning of audio list if we've reached the end
            i = 0
        else:
            # Advance to the next track
            i = i + 1
        track = audio_taunts[i]
        last_taunt_index = i
    else:
        track = audio_taunts[0]
        last_taunt_index = 0
    print('Playing T{0:03d}.mp3'.format(audio_taunts[i - 1]))
    mp3_trigger.play_track(track)


def handle_rf_d(pin):
    print('Pressed RF D - Reset game state')
    global playing
    playing = False


if __name__ == '__main__':
    try:
        # Initial setup
        print('Starting up')
        mp3_trigger.set_volume(0x05)

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        # Configure GPIO pin modes for each connected device type
        print('Configuring pins')
        for pin in [PUTT_SENSOR_PIN, CUP_SENSOR_PIN]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for pin in [RF_RX_A_PIN, RF_RX_B_PIN, RF_RX_C_PIN, RF_RX_D_PIN]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(SERVO_PIN, GPIO.OUT)

        # Add interrupts
        # RF module pins go high for as long as the keyfob button is held.
        print('Adding interrupts')

        # IR sensor output is default high, and IR sensors are *NOT* inverted, just level shifted from 5V to 3.3V
        GPIO.add_event_detect(PUTT_SENSOR_PIN, GPIO.FALLING, callback=handle_putt, bouncetime=1000)
        GPIO.add_event_detect(CUP_SENSOR_PIN, GPIO.FALLING, callback=handle_cup, bouncetime=1000)

        # RF receiver output is default low, but inverted by Schmitt trigger then level shifted from 5V to 3.3V.
        # Pins remain changed for as long as the keyfob button is held down.
        GPIO.add_event_detect(RF_RX_A_PIN, GPIO.FALLING, callback=handle_rf_a, bouncetime=1000)
        GPIO.add_event_detect(RF_RX_B_PIN, GPIO.FALLING, callback=handle_rf_b, bouncetime=1000)
        GPIO.add_event_detect(RF_RX_C_PIN, GPIO.FALLING, callback=handle_rf_c, bouncetime=1000)
        GPIO.add_event_detect(RF_RX_D_PIN, GPIO.FALLING, callback=handle_rf_d, bouncetime=1000)

        # Run the event loop
        loop = asyncio.get_event_loop()
        print('Awaiting putt')
        loop.run_forever()
        loop.close()
    except KeyboardInterrupt:
        sys.exit()
