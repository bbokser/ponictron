import rotaryio


class Encoder:
    """
    Handles encoder
    """

    def __init__(self, pinA, pinB):
        # encoder
        self.encoder = rotaryio.IncrementalEncoder(pinA, pinB, divisor=2)
        self.zero_pos = self.encoder.position

    def rezero(self):
        # re-zero encoder
        self.zero_pos = self.encoder.position

    def get_encoder_pos(self):
        # encoder feedback
        return self.encoder.position - self.zero_pos


from adafruit_seesaw import digitalio, rotaryio
from busio import I2C

from adafruit_seesaw.seesaw import Seesaw


class SeesawEncoder:
    """
    Handles independent i2c encoder
    """

    def __init__(self, i2c: I2C, address: int = 0x36):
        seesaw_device = Seesaw(i2c, addr=address)  # address)
        seesaw_device.pin_mode(24, seesaw_device.INPUT_PULLUP)
        self.button = digitalio.DigitalIO(seesaw_device, 24)

        self.button_prev = False
        self.encoder = rotaryio.IncrementalEncoder(seesaw_device)
        self.zero_pos = self.encoder.position

    def rezero(self):
        # re-zero encoder
        self.zero_pos = self.encoder.position

    def get_encoder_pos(self):
        # encoder feedback
        return self.encoder.position - self.zero_pos

    def update_button(self) -> bool:
        # this must run every timestep to work
        if self.button_prev is True and self._get_button() is False:
            # button was previously pressed, is no longer pressed
            self.button_prev = False
            return True
        self.button_prev = self._get_button()
        return False

    def _get_button(self) -> bool:
        return not self.button.value
