#!/usr/bin/env python3

from qwiic import Relay, MP3Trigger
from time import sleep


I2C_BUS = 1
RELAY_ADDRESS = 0x18
MP3_ADDRESS = 0x37
relay = Relay(I2C_BUS, RELAY_ADDRESS)
mp3 = MP3Trigger(I2C_BUS, MP3_ADDRESS)

mp3.set_volume(0x01)
mp3.play_track(0x02)
sleep(2)
mp3.play_track(0x01)

while True:
    relay.on()
    sleep(1)
    relay.off()
    sleep(1)
