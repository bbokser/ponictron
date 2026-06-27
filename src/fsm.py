import utils
from disp import OPTIONS, LIGHT_OPTIONS


class State:
    def __init__(self, fsm, name):
        self.f = fsm
        self.name = name

    def punch_in(self):
        print("enter ", self.name)

    def enter(self):
        pass

    def execute(self):
        pass

    def exit(self):
        pass

    def punch_out(self):
        print("exit ", self.name)

    def execute_default(self):
        if (
            self.f.clock.alarm1.get_status_init() is True
            or self.f.clock.alarm2.get_status_init() is True
        ):
            self.f.to_transition("toAlarming")


class Alarming(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.clock.alarm1.log_start()
        self.f.clock.alarm2.log_start()

    def execute(self):
        b_enter = self.f.b_enter
        self.f.disp.display_hourmin(self.f.clock.get_hour(), self.f.clock.get_min())
        self.f.buzzer.play(amp=1, on=self.f.heartbeat)

        if not self.f.clock.alarm1.get_status(
            b_enter
        ) and not self.f.clock.alarm2.get_status(b_enter):
            self.f.to_transition("toDefault")

    def exit(self):
        self.f.clock.alarm1.reset()
        self.f.clock.alarm2.reset()
        self.f.buzzer.shutoff()


class Idle(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.disp.switch_to_layer(self.f.disp.layer_main)
        self.pos_init = self.f.encoder.get_encoder_pos()
        self.brightness_init = self.f.disp.get_brightness()
        self.f.disp.set_brightness(0.0)

    def execute(self):
        self.execute_default()
        if self.f.encoder.get_encoder_pos() != self.pos_init:
            self.f.disp.set_brightness(self.brightness_init)
            self.f.to_transition("toDefault")


class Default(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.disp.switch_to_layer(self.f.disp.layer_main)

    def execute(self):
        self.execute_default()
        disp_info = {
            "time": self.f.clock.get_time_str(),
            "weekday": self.f.clock.get_weekday_str(),
            "month": self.f.clock.get_month_str(),
            "day": self.f.clock.get_day_str(),
            "year": self.f.clock.get_year_str(),
            "alarm1": self.f.clock.alarm1.get_str(),
            "alarm1wdays": self.f.clock.alarm1.get_wday_set_str(),
            "alarm2": self.f.clock.alarm2.get_str(),
            "alarm2wdays": self.f.clock.alarm2.get_wday_set_str(),
            "temp": self.f.sensor.get_temperature(),
            "humidity": self.f.sensor.get_humidity(),
            "probe_0_temp": self.f.probe_0.get_temp_str(),
            "probe_1_temp": self.f.probe_1.get_temp_str(),
            "light_timerange": self.f.light.get_timerange_str(),
            "light_brightness": self.f.light.get_brightness_str(),
            "light_brightrange": self.f.light.get_brightrange_str(),
        }
        self.f.disp.update_layer_main(disp_info)
        if self.f.b_save:
            self.f.to_transition("toOptions")
        elif self.f.b_back:
            self.f.to_transition("toIdle")


class Options(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()
        self.option_idx = 0
        self.f.disp.switch_to_layer(self.f.disp.layer_options)

    def execute(self):
        self.execute_default()
        self.option_idx = utils.wrap_to_range(
            self.f.encoder.get_encoder_pos(), 0, len(OPTIONS) - 1
        )
        self.f.disp.update_layer_options(self.option_idx)
        if self.f.b_enter and self.option_idx == 0:
            self.f.to_transition("toSetYear")
        elif self.f.b_enter and self.option_idx == 1:
            self.f.to_transition("toSetHour")
        elif self.f.b_enter and self.option_idx == 2:
            self.f.to_transition("toSetAlarm1Hour")
        elif self.f.b_enter and self.option_idx == 3:
            self.f.to_transition("toSetAlarm2Hour")
        elif self.f.b_enter and self.option_idx == 4:
            self.f.to_transition("toSetBrightness")
        elif self.f.b_enter and self.option_idx == 5:
            self.f.to_transition("toSetUnits")
        elif self.f.b_enter and self.option_idx == 6:
            self.f.to_transition("toSetPitch")
        elif self.f.b_enter and self.option_idx == 7:
            self.f.to_transition("toSetTimeFormat")
        elif self.f.b_enter and self.option_idx == 8:
            self.f.to_transition("toSetLightOpts")
        elif self.f.b_back:
            self.f.to_transition("toDefault")


class LightOptions(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()
        self.lightopt_idx = 0
        self.f.disp.switch_to_layer(self.f.disp.layer_lightopts)

    def execute(self):
        self.execute_default()
        self.lightopt_idx = utils.wrap_to_range(
            self.f.encoder.get_encoder_pos(), 0, len(LIGHT_OPTIONS) - 1
        )
        self.f.disp.update_layer_lightopts(self.lightopt_idx)
        if self.f.b_enter and self.lightopt_idx == 0:
            self.f.to_transition("toSetStartTime")
        elif self.f.b_enter and self.lightopt_idx == 1:
            self.f.to_transition("toSetEndTime")
        elif self.f.b_enter and self.lightopt_idx == 2:
            self.f.to_transition("toSetMaxBright")
        elif self.f.b_enter and self.lightopt_idx == 3:
            self.f.to_transition("toSetMinBright")
        elif self.f.b_enter and self.lightopt_idx == 4:
            self.f.to_transition("toSetSiesta")
        elif self.f.b_back:
            self.f.to_transition("toDefault")


class SetYear(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.year = self.f.clock.get_year()
        self.f.month = self.f.clock.get_month()
        self.f.day = self.f.clock.get_day()
        self.f.encoder.rezero()
        self.f.disp.switch_to_layer(self.f.disp.layer_date)
        self.f.disp.month_date.text = str(self.f.month)
        self.f.disp.day_date.text = str(self.f.day)
        self.f.disp.year_date.color = utils.colors["green"]
        self.f.disp.month_date.color = utils.colors["black"]
        self.f.disp.day_date.color = utils.colors["black"]

    def execute(self):
        self.execute_default()
        self.f.year_new = utils.wrap_to_range(
            self.f.year + self.f.encoder.get_encoder_pos(), a=1970, b=2037
        )
        self.f.disp.year_date.text = str(self.f.year_new)

        if self.f.b_enter:
            self.f.to_transition("toSetMonth")
        elif self.f.b_back:
            self.f.to_transition("toDefault")
        else:
            pass


class SetMonth(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()
        self.f.disp.month_date.color = utils.colors["green"]
        self.f.disp.year_date.color = utils.colors["black"]
        self.f.disp.day_date.color = utils.colors["black"]

    def execute(self):
        self.execute_default()
        self.f.month_new = utils.wrap_to_range(
            self.f.month + self.f.encoder.get_encoder_pos(), a=1, b=12
        )
        self.f.disp.month_date.text = str(self.f.month_new)

        if self.f.b_enter:
            self.f.to_transition("toSetDay")
        elif self.f.b_back:
            self.f.to_transition("toDefault")
        else:
            pass


class SetDay(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()
        self.f.disp.day_date.color = utils.colors["green"]
        self.f.disp.month_date.color = utils.colors["black"]
        self.f.disp.year_date.color = utils.colors["black"]

    def execute(self):
        self.execute_default()
        day_max = utils.get_max_day(year=self.f.year_new, month=self.f.month_new)
        self.f.day_new = utils.wrap_to_range(
            self.f.day + self.f.encoder.get_encoder_pos(), a=1, b=day_max
        )
        self.f.disp.day_date.text = str(self.f.day_new)
        if self.f.b_enter:
            self.f.clock.set_date(
                year=self.f.year_new, month=self.f.month_new, day=self.f.day_new
            )
            self.f.to_transition("toDefault")
        elif self.f.b_back:
            self.f.to_transition("toDefault")
        else:
            pass


class SetHour(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.hour = self.f.clock.get_hour()
        self.f.minute = self.f.clock.get_min()
        self.f.encoder.rezero()
        self.f.disp.enter_layer_time_hour(min="{:02d}".format(self.f.minute))

    def execute(self):
        self.execute_default()
        self.f.hour_new = (self.f.hour + self.f.encoder.get_encoder_pos()) % 24
        self.f.disp.time_hour.text = "{:d}".format(self.f.hour_new)

        if self.f.b_enter:
            self.f.to_transition("toSetMin")
        elif self.f.b_back:
            self.f.to_transition("toDefault")
        else:
            pass


class SetMin(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()
        self.f.disp.enter_layer_time_min(hour=str(self.f.hour_new))

    def execute(self):
        self.execute_default()
        self.f.min_new = (self.f.minute + self.f.encoder.get_encoder_pos()) % 60
        self.f.disp.time_min.text = "{:02d}".format(self.f.min_new)

        if self.f.b_enter:
            self.f.clock.set_time(hour=self.f.hour_new, min=self.f.min_new)
            self.f.to_transition("toDefault")
        elif self.f.b_back:
            self.f.to_transition("toDefault")
        else:
            pass


class SetAlarmHour(State):
    def __init__(
        self,
        fsm,
        name,
        alarm,
        transition: str = "toSetAlarm1Min",
    ):
        """
        transition: Next state
        """
        super().__init__(fsm, name)
        self.alarm = alarm
        self.transition = transition

    def enter(self):
        self.f.hour = self.alarm.get_hour()
        self.f.minute = self.alarm.get_min()
        self.f.encoder.rezero()
        self.f.disp.enter_layer_time_hour(min=str(self.f.minute))

    def execute(self):
        self.execute_default()
        self.f.hour_new = (self.f.hour + self.f.encoder.get_encoder_pos()) % 24
        self.f.disp.time_hour.text = "{:d}".format(self.f.hour_new)

        if self.f.b_enter:
            self.f.to_transition(self.transition)
        elif self.f.b_back:
            self.alarm.disable()
            self.f.to_transition("toDefault")


class SetAlarmMin(State):
    def __init__(
        self,
        fsm,
        name,
        alarm,
        transition: str = "toSetAlarm1Wdays",
    ):
        super().__init__(fsm, name)
        self.alarm = alarm
        self.transition = transition

    def enter(self):
        self.f.encoder.rezero()
        self.f.disp.enter_layer_time_min(hour=str(self.f.hour_new))

    def execute(self):
        self.execute_default()
        self.f.min_new = (self.f.minute + self.f.encoder.get_encoder_pos()) % 60
        self.f.disp.time_min.text = "{:02d}".format(self.f.min_new)

        if self.f.b_enter:
            self.f.to_transition(self.transition)
        elif self.f.b_back:
            self.alarm.disable()
            self.f.to_transition("toDefault")


class SetAlarmWdays(State):
    def __init__(self, fsm, name, alarm, wday_idx: int, transition: str):
        super().__init__(fsm, name)
        self.alarm = alarm
        self.wday_idx = wday_idx
        self.transition = transition

    def enter(self):
        self.f.encoder.rezero()
        if self.wday_idx == 0:
            self.f.wday_set_new = list(self.alarm.wday_set)
        self.f.disp.switch_to_layer(self.f.disp.layer_value)
        self.f.disp.update_layer_value_title("Alarm Weekdays")

    def execute(self):
        self.execute_default()
        self.f.wday_set_new[self.wday_idx] = (
            self.alarm.wday_set[self.wday_idx] + self.f.encoder.get_encoder_pos()
        ) % 2
        self.f.disp.update_layer_value(
            value=utils.weekday[self.wday_idx]
            + ": "
            + str(bool(self.f.wday_set_new[self.wday_idx]))
        )
        if (self.f.b_enter and self.wday_idx == 6) or self.f.b_save:
            self.alarm.set_alarm(
                hour=self.f.hour_new, min=self.f.min_new, wday_set=self.f.wday_set_new
            )
            self.f.to_transition("toDefault")
        elif self.f.b_enter and self.wday_idx < 6:
            self.f.to_transition(self.transition)
        elif self.f.b_back:
            self.f.clock.alarm1.disable()
            self.f.to_transition("toDefault")


class SetBrightness(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()
        self.f.brightness_original = self.f.disp.get_brightness()
        self.f.disp.switch_to_layer(self.f.disp.layer_value)
        self.f.disp.update_layer_value_title("Display Brightness")

    def execute(self):
        self.execute_default()
        # minimum of 1 to prevent blinking from doing nothing
        count_max = 9
        self.f.disp.set_brightness(
            utils.percentize(
                utils.wrap_to_range(
                    self.f.brightness_original + self.f.encoder.get_encoder_pos(),
                    1,
                    count_max,
                ),
                0,
                count_max,
            )
            ** 2
        )
        self.f.disp.update_layer_value(value=self.f.disp.get_brightness())

        if self.f.b_enter:
            self.f.to_transition("toDefault")
        elif self.f.b_back:
            self.f.disp.set_brightness(self.f.brightness_original)
            self.f.to_transition("toDefault")


class SetUnits(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()
        self.f.units_new = self.f.sensor.units
        self.f.disp.switch_to_layer(self.f.disp.layer_value)
        self.f.disp.update_layer_value_title("Units")

    def execute(self):
        self.execute_default()
        self.f.units_new = (self.f.sensor.units + self.f.encoder.get_encoder_pos()) % 2
        if self.f.units_new == 1:
            self.f.disp.update_layer_value("Fahrenheit")
        else:
            self.f.disp.update_layer_value("Celsius")

        if self.f.b_enter:
            self.f.sensor.change_units(self.f.units_new)
            self.f.to_transition("toDefault")
        elif self.f.b_back:
            self.f.to_transition("toDefault")


class SetPitch(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()
        self.f.pitch_new = self.f.buzzer.pitch
        self.f.disp.switch_to_layer(self.f.disp.layer_value)
        self.f.disp.update_layer_value_title("Pitch")

    def execute(self):
        self.execute_default()
        # https://www.mouser.com/datasheet/2/1628/css_i4b20_smt_tr-3509940.pdf
        self.f.pitch_new = int(
            utils.wrap_to_range(
                int(self.f.buzzer.pitch / 50) + self.f.encoder.get_encoder_pos(), 1, 10
            )
            * 50
        )
        self.f.disp.update_layer_value(self.f.pitch_new)
        self.f.buzzer.play(amp=0.25, pitch=self.f.pitch_new)

        if self.f.b_enter:
            self.f.buzzer.pitch = self.f.pitch_new
            self.f.to_transition("toDefault")
        elif self.f.b_back:
            self.f.to_transition("toDefault")

    def exit(self):
        self.f.buzzer.shutoff()


class SetTimeFormat(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):

        self.f.encoder.rezero()
        self.f.format_new = self.f.format
        self.f.disp.switch_to_layer(self.f.disp.layer_value)
        self.f.disp.update_layer_value_title("Time Format")

    def execute(self):
        self.execute_default()
        self.f.format_new = (self.f.format + self.f.encoder.get_encoder_pos()) % 2
        if self.f.format_new == 0:
            self.f.disp.update_layer_value("24 Hr")
        else:
            self.f.disp.update_layer_value("12 Hr")

        if self.f.b_enter:
            self.f.format = self.f.format_new
            self.f.clock.alarm1.change_format(self.f.format)
            self.f.clock.alarm2.change_format(self.f.format)
            self.f.clock.change_format(self.f.format)
            self.f.to_transition("toDefault")
        elif self.f.b_back:
            self.f.to_transition("toDefault")


class SetStartTime(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.hour = int(self.f.light.start_time)
        self.f.minute = 0
        self.f.encoder.rezero()
        self.f.disp.enter_layer_time_hour(min="{:02d}".format(self.f.minute))

    def execute(self):
        self.execute_default()
        self.f.hour_new = (self.f.hour + self.f.encoder.get_encoder_pos()) % 24
        self.f.disp.time_hour.text = "{:d}".format(self.f.hour_new)

        if self.f.b_enter:
            self.f.light.start_time = self.f.hour_new
            self.f.light.recalculate()
            self.f.to_transition("toDefault")
        elif self.f.b_back:
            self.f.to_transition("toDefault")
        else:
            pass


class SetEndTime(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.hour = int(self.f.light.end_time)
        self.f.minute = 0
        self.f.encoder.rezero()
        self.f.disp.enter_layer_time_hour(min="{:02d}".format(self.f.minute))

    def execute(self):
        self.execute_default()
        self.f.hour_new = (self.f.hour + self.f.encoder.get_encoder_pos()) % 24
        self.f.disp.time_hour.text = "{:d}".format(self.f.hour_new)

        if self.f.b_enter:
            self.f.light.end_time = self.f.hour_new
            self.f.light.recalculate()
            self.f.to_transition("toDefault")
        elif self.f.b_back:
            self.f.to_transition("toDefault")
        else:
            pass


class SetMaxBright(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()
        self.f.brightness_original = self.f.light.brightness_max
        self.f.disp.switch_to_layer(self.f.disp.layer_value)
        self.f.disp.update_layer_value_title("Max Light Brightness")

    def execute(self):
        self.execute_default()
        # minimum of 1 to prevent blinking from doing nothing
        count_max = 9
        self.f.light.brightness_max = (
            utils.percentize(
                utils.wrap_to_range(
                    self.f.brightness_original + self.f.encoder.get_encoder_pos(),
                    1,
                    count_max,
                ),
                0,
                count_max,
            )
            ** 2
        )
        self.f.disp.update_layer_value(value=self.f.light.brightness_max)

        if self.f.b_enter:
            self.f.to_transition("toDefault")
            self.f.light.recalculate()
        elif self.f.b_back:
            self.f.light.brightness_max = self.f.brightness_original
            self.f.to_transition("toDefault")


class SetMinBright(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()
        self.f.brightness_original = self.f.light.brightness_min
        self.f.disp.switch_to_layer(self.f.disp.layer_value)
        self.f.disp.update_layer_value_title("Min Light Brightness")

    def execute(self):
        self.execute_default()
        # minimum of 1 to prevent blinking from doing nothing
        count_max = 9
        self.f.light.brightness_min = (
            utils.percentize(
                utils.wrap_to_range(
                    self.f.brightness_original + self.f.encoder.get_encoder_pos(),
                    1,
                    count_max,
                ),
                0,
                count_max,
            )
            ** 2
        )
        self.f.disp.update_layer_value(value=self.f.light.brightness_min)

        if self.f.b_enter:
            self.f.to_transition("toDefault")
            self.f.light.recalculate()
        elif self.f.b_back:
            self.f.light.brightness_min = self.f.brightness_original
            self.f.to_transition("toDefault")


class SetSiesta(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.hour = int(self.f.light.siesta)
        self.f.minute = 0
        self.f.encoder.rezero()
        self.f.disp.enter_layer_time_hour(min="{:02d}".format(self.f.minute))

    def execute(self):
        self.execute_default()
        self.f.hour_new = (self.f.hour + self.f.encoder.get_encoder_pos()) % 24
        self.f.disp.time_hour.text = "{:d}".format(self.f.hour_new)

        if self.f.b_enter:
            self.f.light.siesta = self.f.hour_new
            self.f.light.recalculate()
            self.f.to_transition("toDefault")
        elif self.f.b_back:
            self.f.to_transition("toDefault")
        else:
            pass


class Transition:
    def __init__(self, tostate):
        self.toState = tostate

    def execute(self):
        # return self.toState
        pass


class FSM:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

        self.states = {}
        self.transitions = {}
        self.curState = None
        self.prevState = None
        self.trans = None

        self.add_state("options", Idle)
        self.add_state("default", Default)
        self.add_state("alarming", Alarming)
        self.add_state("set_year", SetYear)
        self.add_state("set_month", SetMonth)
        self.add_state("set_day", SetDay)
        self.add_state("set_hour", SetHour)
        self.add_state("set_min", SetMin)
        self.add_state(
            "set_alarm1_hour",
            SetAlarmHour,
            alarm=self.clock.alarm1,
            transition="toSetAlarm1Min",
        )
        self.add_state(
            "set_alarm1_min",
            SetAlarmMin,
            alarm=self.clock.alarm1,
            transition="toSetAlarm1Wday0",
        )
        self.add_state(
            "set_alarm2_hour",
            SetAlarmHour,
            alarm=self.clock.alarm2,
            transition="toSetAlarm2Min",
        )
        self.add_state(
            "set_alarm2_min",
            SetAlarmMin,
            alarm=self.clock.alarm2,
            transition="toSetAlarm2Wday0",
        )
        for i in range(7):
            self.add_state(
                "set_alarm1_wday" + str(i),
                SetAlarmWdays,
                alarm=self.clock.alarm1,
                wday_idx=i,
                transition="toSetAlarm1Wday" + str(i + 1),
            )
            self.add_state(
                "set_alarm2_wday" + str(i),
                SetAlarmWdays,
                alarm=self.clock.alarm2,
                wday_idx=i,
                transition="toSetAlarm2Wday" + str(i + 1),
            )

        self.add_state("set_brightness", SetBrightness)
        self.add_state("set_units", SetUnits)
        self.add_state("set_pitch", SetPitch)
        self.add_state("set_time_format", SetTimeFormat)
        self.add_state("set_light_options", LightOptions)
        self.add_state("options", Options)

        self.add_transition("toIdle", Transition("idle"))
        self.add_transition("toOptions", Transition("options"))
        self.add_transition("toAlarming", Transition("alarming"))
        self.add_transition("toSetYear", Transition("set_year"))
        self.add_transition("toSetMonth", Transition("set_month"))
        self.add_transition("toSetDay", Transition("set_day"))
        self.add_transition("toSetHour", Transition("set_hour"))
        self.add_transition("toSetMin", Transition("set_min"))
        self.add_transition("toSetAlarm1Hour", Transition("set_alarm1_hour"))
        self.add_transition("toSetAlarm1Min", Transition("set_alarm1_min"))
        self.add_transition("toSetAlarm2Hour", Transition("set_alarm2_hour"))
        self.add_transition("toSetAlarm2Min", Transition("set_alarm2_min"))
        self.add_transition("toSetBrightness", Transition("set_brightness"))
        self.add_transition("toSetUnits", Transition("set_units"))
        self.add_transition("toSetPitch", Transition("set_pitch"))
        self.add_transition("toSetTimeFormat", Transition("set_time_format"))
        self.add_transition("toSetLightOpts", Transition("set_light_options"))

        self.add_state("set_start_time", SetStartTime)
        self.add_state("set_end_time", SetEndTime)
        self.add_state("set_max_bright", SetMaxBright)
        self.add_state("set_min_bright", SetMinBright)
        self.add_state("set_siesta", SetSiesta)

        self.add_transition("toSetStartTime", Transition("set_start_time"))
        self.add_transition("toSetEndTime", Transition("set_end_time"))
        self.add_transition("toSetMaxBright", Transition("set_max_bright"))
        self.add_transition("toSetMinBright", Transition("set_min_bright"))
        self.add_transition("toSetSiesta", Transition("set_siesta"))

        self.add_transition("toDefault", Transition("default"))
        for i in range(7):
            self.add_transition(
                "toSetAlarm1Wday" + str(i),
                Transition("set_alarm1_wday" + str(i)),
            )
            self.add_transition(
                "toSetAlarm2Wday" + str(i),
                Transition("set_alarm2_wday" + str(i)),
            )

        self.setstate("default")

    def add_transition(self, transname, transition):
        self.transitions[transname] = transition

    def add_state(self, statename, state, **kwargs):
        self.states[statename] = state(self, statename, **kwargs)

    def setstate(self, statename):
        # look for whatever state we passed in within the states dict
        self.prevState = self.curState
        self.curState = self.states[statename]

    def to_transition(self, to_trans):
        # set the transition state
        self.trans = self.transitions[to_trans]

    def execute(self):
        if self.trans:
            self.curState.exit()
            if self.verbose is True:
                self.curState.punch_out()
            self.trans.execute()
            self.setstate(self.trans.toState)
            if self.verbose is True:
                self.curState.punch_in()
            self.curState.enter()
            self.trans = None

        self.curState.execute()
