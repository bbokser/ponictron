from adafruit_ds18x20 import DS18X20


class Probe:
    def __init__(self, ow_bus, index: int) -> None:

        self.ds18 = DS18X20(ow_bus, ow_bus.scan()[index])

    def get_temp_str(self) -> str:
        try:
            temp = self.ds18.temperature
        except Exception:
            temp = None
        return str(temp)
