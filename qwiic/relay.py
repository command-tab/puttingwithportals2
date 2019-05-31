from smbus2 import SMBus


class Relay(object):

    COMMAND_RELAY_OFF = 0x00
    COMMAND_RELAY_ON = 0x01
    COMMAND_SET_ADDRESS = 0x03

    def __init__(self, bus_number, device_address):
        self.bus = SMBus(bus_number)
        self.device_address = device_address

    def __del__(self):
        self.bus.close()

    def off(self):
        """
        Turns the relay off
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_RELAY_OFF, 0x01)

    def on(self):
        """
        Turns the relay on
        """
        self.bus.write_byte_data(self.device_address, self.COMMAND_RELAY_ON, 0x01)

    def set_address(self, address):
        """
        Sets the I2C address of Qwiic Relay.
        """
        if address < 0x07 or address > 0x78:
            raise ValueError('Invalid I2C address')
        self.bus.write_byte_data(self.device_address, self.COMMAND_SET_ADDRESS, address)
        sleep(0.05)
