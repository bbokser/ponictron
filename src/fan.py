import pwmio


class Fan:
    def __init__(self, pin, speed=1) -> None:
        self.fan = pwmio.PWMOut(pin, frequency=5000, duty_cycle=0)
        self.set_speed(speed)

    def set_speed(self, percent: float) -> None:
        assert 0 <= percent <= 1
        self._saved_duty_cycle = int(percent * 65535)
        self.on()

    def get_speed(self) -> float:
        return self._saved_duty_cycle

    def on(self):
        self.fan.duty_cycle = self._saved_duty_cycle

    def off(self) -> None:
        self.fan.duty_cycle = 0
