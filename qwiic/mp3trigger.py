from smbus2 import SMBus
from time import sleep


class MP3Trigger(object):

    COMMAND_STOP = 0x00
    COMMAND_PLAY_TRACK = 0x01
    COMMAND_PLAY_FILENUMBER = 0x02
    COMMAND_PAUSE = 0x03
    COMMAND_PLAY_NEXT = 0x04
    COMMAND_PLAY_PREVIOUS = 0x05
    COMMAND_SET_EQ = 0x06
    COMMAND_SET_VOLUME = 0x07
    COMMAND_GET_SONG_COUNT = 0x08
    COMMAND_GET_SONG_NAME = 0x09
    COMMAND_GET_PLAY_STATUS = 0x0A
    COMMAND_GET_CARD_STATUS = 0x0B
    COMMAND_GET_VERSION = 0x0C
    COMMAND_CLEAR_INTERRUPTS = 0x0D
    COMMAND_GET_VOLUME = 0x0E
    COMMAND_GET_EQ = 0x0F
    COMMAND_GET_ID = 0x10
    COMMAND_SET_ADDRESS = 0xC7

    EQ_NORMAL = 0
    EQ_POP = 1
    EQ_ROCK = 2
    EQ_JAZZ = 3
    EQ_CLASSICAL = 4
    EQ_BASS = 5

    def __init__(self, bus_number, device_address):
        self.bus = SMBus(bus_number)
        self.device_address = device_address

    def __del__(self):
        self.bus.close()

    def stop(self):
        """
        Stops any currently playing track
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_STOP)

    def play_track(self, track_number):
        """
        Play a given track number (like on a CD).
        For example, 0x0A will play the 10th MP3 file in the root directory.
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_PLAY_TRACK, track_number)

    def play_file(self, file_number):
        """
        Play a file # from the root directory. For example, 0x03 will play F003.mp3.
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_PLAY_FILENUMBER, file_number)

    def pause(self):
        """
        Pause if playing, or starting playing if paused
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_PAUSE)

    def play_next(self):
        """
        Play the next file (next track) located in the root directory
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_PLAY_NEXT)

    def play_previous(self):
        """
        Play the previous file (previous track) located in the root directory
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_PLAY_PREVIOUS)

    def set_eq(self, eq):
        """
        Set the equalization level to one of 6 settings.
        Setting is stored to NVM and is loaded at each power-on.
        """
        if eq not in [self.EQ_NORMAL, self.EQ_POP, self.EQ_ROCK, self.EQ_JAZZ, self.EQ_CLASSICAL, self.EQ_BASS]:
            raise ValueError('Invalid EQ setting')
        self.bus.write_byte_data(self.device_address, self.COMMAND_SET_EQ, eq)

    def get_eq(self):
        """
        Returns byte that represents the EQ setting.
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_GET_ID)
        sleep(0.05)
        return self.bus.read_byte_data(self.device_address, 0)

    def set_volume(self, volume_level):
        """
        Set volume level to one of 32 settings: 0 = Off, 31 = Max volume.
        Setting is stored to NVM and is loaded at each power-on.
        """
        if volume_level < 0 or volume_level > 31:
            raise ValueError('Invalid volume level')
        self.bus.write_byte_data(self.device_address, self.COMMAND_SET_VOLUME, volume_level)

    def get_volume(self):
        """
        Returns byte that represents the volume level
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_GET_VOLUME)
        sleep(0.05)
        return self.bus.read_byte_data(self.device_address, 0)

    def get_song_count(self):
        """
        Returns one byte representing the number of MP3s found on the microSD card. 255 max.
        Note: Song count is established at power-on. After loading files on the SD card via USB
        be sure to power-cycle the board to update this value. Note: This causes song to stop playing.
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_GET_SONG_COUNT)
        sleep(0.05)
        return self.bus.read_byte_data(self.device_address, 0)

    def get_song_name(self):
        """
        Returns the first 8 characters of the file currently being played. Once the command is issued,
        the MP3 Trigger must be given 50ms to acquire the song name before it can be queried with an I2C read.
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_GET_SONG_NAME)
        sleep(0.05)
        return self.bus.read_byte_data(self.device_address, 0)

    def get_id(self):
        """
        Returns 0x39. Useful for testing if a device at a given I2C address is indeed an MP3 Trigger.
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_GET_ID)
        sleep(0.05)
        return self.bus.read_byte_data(self.device_address, 0)

    def get_card_status(self):
        """
        Returns a byte indicating card status. 0 = OK, 5 = SD Error. Once the command is issued,
        the MP3 Trigger must be given 50ms to acquire the card status before it can be queried with an I2C read.
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_GET_CARD_STATUS)
        sleep(0.05)
        return self.bus.read_byte_data(self.device_address, 0)

    def get_version(self):
        """
        Returns two bytes indicating Major and Minor firmware version.
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_GET_VERSION)
        sleep(0.05)
        return self.bus.read_byte_data(self.device_address, 0)

    def clear_interrupts(self):
        """
        Clears the interrupt bit.
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_CLEAR_INTERRUPTS)

    def get_play_status(self):
        """
        Returns a byte indicating MP3 player status. 0 = OK, 1 = Fail, 2 = No such file, 5 = SD Error.
        """
        return self.bus.read_byte_data(self.device_address, self.COMMAND_GET_PLAY_STATUS)

    def set_address(self, address):
        """
        Sets the I2C address of Qwiic MP3 Trigger. For example, 0x6E 0xC7 0x21 will change the MP3 Trigger at I2C address
        0x37 to address 0x21. In this example 0x6E is device address 0x37 with write bit set to 1. Valid addresses
        are 0x08 to 0x77 inclusive. Setting is stored to NVM and is loaded at each power-on.
        """
        if address < 0x07 or address > 0x78:
            raise ValueError('Invalid I2C address')
        self.bus.write_byte_data(self.device_address, self.COMMAND_CHANGE_ADDRESS, address)
