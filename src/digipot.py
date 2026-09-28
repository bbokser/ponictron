import adafruit_ds3502
from busio import I2C

from utils import percentize


class DigiPot:
    def __init__(self, i2c: I2C):
        self.ds3502 = adafruit_ds3502.DS3502(i2c)

    def set_value(self, value: float):
        """Set resistance value. Input must be between 0 and 10000"""
        self.ds3502.wiper = int(127 * (1 - percentize(value, 0.0, 10000.0)))
