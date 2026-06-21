import time
import board
import busio
from adafruit_onewire.bus import OneWireBus
from fsm import FSM

# hardware
from disp import Disp
from clock import Clock

from encoder import SeesawEncoder
from buzzer import Buzzer
from button import PinButton
from sense_ht import HTSensor
from led import LED
from dac import DAC
from probe import Probe
from light import Light
from micro_sd import MicroSD
from fan import Fan
# time.sleep(5)  # to ensure serial connection does not fail


class OS(FSM):
    def __init__(self, verbose):
        # initialize class objects
        i2c = busio.I2C(scl=board.GP5, sda=board.GP4, frequency=50000)
        spi = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=None)
        ow_bus = OneWireBus(board.GP3)
        self.clock = Clock(i2c)
        # this has to run after clock is created
        super().__init__(verbose=verbose)
        # disable the alarms on reset because I haven't figured out how to retrieve the saved info from the rtc
        # self.clock.alarm1.disable()
        # self.clock.alarm2.disable()
        self.button_2 = PinButton(board.GP10)  # the upper one
        self.button_1 = PinButton(board.GP11)  # the lower one
        self.encoder = SeesawEncoder(i2c, address=0x36)
        self.buzzer = Buzzer(board.GP21)
        self.sensor = HTSensor(i2c, address=0x45, units=0)
        self.dac = DAC(i2c)
        self.probe_0 = Probe(ow_bus, 0)
        self.probe_1 = Probe(ow_bus, 1)
        self.micro_sd = MicroSD(spi, cs=board.GP20)
        self.light = Light(
            self.clock,
            start_time=8.0,
            end_time=20.0,
            brightness_min=0.15,
            brightness_max=0.6,
        )
        # board.LED clashes with GP9 pwm slice
        # self.led = LED(board.LED)
        self.fan = Fan(board.GP22, speed=0.2)
        self.disp = Disp(
            spi=spi,
            cs=board.GP17,
            dc=board.GP8,
            reset=board.GP13,
            backlight=board.GP9,
        )

        # 24 vs 12 hour format
        self.format = 0
        self.format_new = 0

        self.wday_idx = 0
        self.wday_set_new = [0] * 7
        self.dt = 0.1
        self.beat_rate = 0.3  # should be a multiple of dt
        self.dac.set_value(self.light.get_brightness())

    def run(self):
        z = 0
        k = 0
        self.heartbeat = True
        k_beat = int(self.beat_rate / self.dt)

        j = 0
        # how many seconds before refresh
        refresh_time = 10 * 60
        refresh_counter = int(refresh_time / self.dt)
        # reheat the sensor chip once per day
        reheat_counter = int(24 * 60 * 60 / refresh_time)

        while True:
            if k >= k_beat:
                k = 0
                self.heartbeat = not self.heartbeat
            # self.led.blink(self.heartbeat)
            self.b_enter = self.encoder.update_button()
            self.b_save = self.button_2.update()
            self.b_back = self.button_1.update()
            self.execute()
            self.disp.update()
            if j > refresh_counter:
                self.dac.set_value(self.light.get_brightness())
                if z == 0:
                    self.sensor.set_mode_read()
                j = 0
                z += 1
                if z > reheat_counter:
                    self.sensor.set_mode_heat()
                    z = 0
            k += 1
            j += 1
            time.sleep(self.dt)


if __name__ == "__main__":
    verbose = True
    os = OS(verbose)
    os.run()
