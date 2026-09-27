import keypad


class PinButton:
    """
    Debounces button presses from pin
    """

    def __init__(self, pin):
        self.keys = keypad.Keys((pin,), value_when_pressed=False, pull=True)
        self.event = keypad.Event()

    def update(self) -> bool:
        # Check if event was queued in bg since last loop
        return bool(self.keys.events.get_into(self.event) and self.event.pressed)
