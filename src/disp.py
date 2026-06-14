import utils

# import gc  # garbage collector
# print('free memory left before (most) imports: ', gc.mem_free())
# from ulab import numpy as np
import displayio
import vectorio
from fourwire import FourWire
import adafruit_ili9341
import supervisor
from adafruit_display_text.bitmap_label import Label
from font_ostrich_sans_black_24 import FONT as font_small
from font_ostrich_sans_black_60 import FONT as font_large

# print('free memory left after imports: ', gc.mem_free())

supervisor.runtime.autoreload = False

displayio.release_displays()

OPTIONS = [
    "Year",
    "Time",
    "Alarm1",
    "Alarm2",
    "Brightness",
    "Units",
    "Pitch",
    "Time Format",
]
ALIGN = {
    "left": (0.0, 1.0),
    "center": (0.5, 1.0),
    "right": (1.0, 1.0),
}


class Disp:
    def __init__(self, spi, cs, dc, reset):

        # epd_busy = board.GP16
        display_bus = FourWire(
            spi, command=dc, chip_select=cs, reset=reset, baudrate=1000000
        )
        display = adafruit_ili9341.ILI9341(
            display_bus, width=320, height=240, rotation=180
        )

        # create palette
        color_list = list(utils.colors.values())
        self.color_names = list(utils.colors.keys())
        n = len(color_list)
        p = displayio.Palette(n)
        for i in range(0, n):
            p[i] = color_list[i]
        self.p = p

        self.display = display
        self.width = display.width
        self.height = display.height

        self.color_list = color_list
        # should match the smaller font size
        self.size_font_small = 24
        self.size_font_large = 60
        # TODO: implement brightness
        self.brightness = 1

        row_step_size = self.size_font_small
        self.rows = [0] * 8
        self.rows[0] = self.size_font_small - 4
        for i in range(len(self.rows) - 1):
            self.rows[i + 1] = self.rows[i] + row_step_size

        self.x_center = self.display.width // 2
        self.cols = [5, self.x_center + int(self.x_center / 4)]
        self.offset_txt = 24
        self.offset_icon = 18
        self.create_layer_main()
        self.create_layer_date()
        self.create_layer_options()
        self.create_layer_time()
        self.create_layer_value()
        self.switch_to_layer(self.layer_main)

    def gen_icon_label_pair(self, col: int, row: int, bmp: str) -> tuple[Label, Label]:
        icon = self.create_bmp(
            bmp, x=self.cols[col], y=self.rows[row] - self.offset_icon
        )
        label = self.create_label(
            x=self.cols[col] + self.offset_txt,
            y=self.rows[row],
        )
        return icon, label

    def create_layer_main(self) -> None:
        # column 1
        self.bg_main = self.create_bg(color="white")
        self.date_main = self.create_label(
            x=self.cols[0],
            y=self.rows[0],
        )
        self.time_main = self.create_label(
            x=self.cols[0],
            y=self.rows[1],
        )
        self.alarm1_icon_main, self.alarm1_main = self.gen_icon_label_pair(
            col=0, row=2, bmp="/bmps/alarm1.bmp"
        )
        self.alarm2_icon_main, self.alarm2_main = self.gen_icon_label_pair(
            col=0, row=3, bmp="/bmps/alarm2.bmp"
        )
        self.light_icon_main, self.light_main = self.gen_icon_label_pair(
            col=0, row=4, bmp="/bmps/elec.bmp"
        )
        self.light_timerange_icon_main, self.light_timerange_main = (
            self.gen_icon_label_pair(col=0, row=5, bmp="/bmps/elec.bmp")
        )

        # column 2
        # self.create_bmp("/bmps/elec.bmp", x=col_2, y=row_1 - offset_icon)
        self.hum_icon_main, self.hum_main = self.gen_icon_label_pair(
            col=1, row=0, bmp="/bmps/humidity.bmp"
        )
        self.temp_icon_main, self.temp_main = self.gen_icon_label_pair(
            col=1, row=1, bmp="/bmps/temp.bmp"
        )
        self.probe0_icon_main, self.probe0_main = self.gen_icon_label_pair(
            col=1, row=2, bmp="/bmps/temp.bmp"
        )
        self.probe1_icon_main, self.probe1_main = self.gen_icon_label_pair(
            col=1, row=3, bmp="/bmps/temp.bmp"
        )
        objects = [
            self.bg_main,
            self.date_main,
            self.time_main,
            self.alarm1_icon_main,
            self.alarm2_icon_main,
            self.alarm1_main,
            self.alarm2_main,
            self.probe0_icon_main,
            self.probe0_main,
            self.probe1_icon_main,
            self.probe1_main,
            self.temp_icon_main,
            self.temp_main,
            self.hum_icon_main,
            self.hum_main,
            self.light_icon_main,
            self.light_main,
            self.light_timerange_icon_main,
            self.light_timerange_main,
        ]
        self.layer_main = displayio.Group()
        for object in objects:
            self.layer_main.append(object)

    def create_layer_date(self) -> None:
        self.bg_date = self.create_bg(color="white")
        self.yearlabel_date = self.create_label(
            text="Year:",
            x=self.display.width // 2,
            y=self.rows[1],
            align="right",
        )
        self.year_date = self.create_label(
            x=self.display.width // 2,
            y=self.rows[1],
            align="left",
        )
        self.monthlabel_date = self.create_label(
            text="Month:",
            x=self.display.width // 2,
            y=self.rows[2],
            align="right",
        )
        self.month_date = self.create_label(
            x=self.display.width // 2,
            y=self.rows[2],
            align="left",
        )
        self.daylabel_date = self.create_label(
            text="Day:",
            x=self.display.width // 2,
            y=self.rows[3],
            align="right",
        )
        self.day_date = self.create_label(
            x=self.display.width // 2,
            y=self.rows[3],
            align="left",
        )
        self.layer_date = displayio.Group()
        objects = [
            self.bg_date,
            self.yearlabel_date,
            self.monthlabel_date,
            self.daylabel_date,
            self.year_date,
            self.month_date,
            self.day_date,
        ]
        for object in objects:
            self.layer_date.append(object)

    def create_layer_options(self) -> None:
        self.bg_options = self.create_bg(color="white")
        x = self.display.width // 2
        self.options = {}
        for i in range(len(self.rows)):
            self.options.setdefault(
                OPTIONS[i],
                self.create_label(text=OPTIONS[i], x=x, y=self.rows[i], align="center"),
            )
        self.layer_options = displayio.Group()
        self.layer_options.append(self.bg_options)
        for x in list(self.options.values()):
            self.layer_options.append(x)

    def create_layer_time(self) -> None:
        self.bg_time = self.create_bg(color="white")
        self.time_hour = self.create_label(
            x=self.display.width // 2 - 2,
            y=self.display.height // 2,
            align="right",
        )
        self.time_colon = self.create_label(
            text=":",
            x=self.display.width // 2,
            y=self.display.height // 2 - 6,
            align="center",
        )
        self.time_min = self.create_label(
            x=self.display.width // 2 + 2,
            y=self.display.height // 2,
            align="left",
        )
        self.layer_time = displayio.Group()
        objects = [self.bg_time, self.time_hour, self.time_colon, self.time_min]
        for object in objects:
            self.layer_time.append(object)

    def create_layer_value(self) -> None:
        self.bg_value = self.create_bg(color="white")
        self.title_value = self.create_label(
            x=self.display.width // 2,
            y=self.display.height // 2 - self.size_font_small // 2,
            align="center",
        )
        self.value_value = self.create_label(
            x=self.display.width // 2,
            y=self.display.height // 2 + self.size_font_small // 2,
            align="center",
        )
        self.layer_value = displayio.Group()
        objects = [self.bg_value, self.title_value, self.value_value]
        for object in objects:
            self.layer_value.append(object)

    ### Updating ###

    def update_layer_main(self, info: dict) -> None:
        self.date_main.text = (
            info["weekday"]
            + ", "
            + info["month"]
            + " "
            + info["day"]
            + " "
            + info["year"]
        )
        self.time_main.text = info["time"]
        self.alarm1_main.text = info["alarm1"] + " " + info["alarm1wdays"]
        self.alarm2_main.text = info["alarm2"] + " " + info["alarm2wdays"]
        self.probe0_main.text = "P0: " + info["probe_0_temp"]
        self.probe1_main.text = "P1: " + info["probe_1_temp"]
        self.temp_main.text = "B: " + info["temp"]
        self.hum_main.text = info["humidity"] + " %"
        self.light_timerange_main.text = "Time Range: " + info["light_timerange"]
        self.light_main.text = info["light_brightness"]

    def update_layer_options(self, option_idx: int) -> None:
        self.options[OPTIONS[option_idx]].color = utils.colors["green"]
        for i in range(len(OPTIONS)):
            if i != option_idx:
                self.options[OPTIONS[i]].color = utils.colors["black"]

    def update_layer_value(self, value: int) -> None:
        self.value_value.text = str(value)

    def update_layer_value_title(self, title: str) -> None:
        self.title_value.text = title

    def enter_layer_time_hour(self, min: str) -> None:
        """Enter the time layer and set minute. Preparing to set hour"""
        self.display.root_group = self.layer_time
        self.time_min.text = min
        self.time_hour.color = utils.colors["green"]
        self.time_min.color = utils.colors["black"]

    def enter_layer_time_min(self, hour: str) -> None:
        """Enter the time layer and set hour. Preparing to set minute"""
        self.time_hour.text = hour
        self.time_min.color = utils.colors["green"]
        self.time_hour.color = utils.colors["black"]

    def switch_to_layer(self, layer: displayio.Group) -> None:
        # show the desired layer
        self.display.root_group = layer

    def update(self) -> None:
        self.display.refresh()

    def get_idx(self, color: str) -> int:
        """
        Convert color name to index
        """
        return self.color_names.index(color)

    def create_bmp(self, path: str, x: int, y: int) -> displayio.TileGrid:
        odb = displayio.OnDiskBitmap(path)
        image = displayio.TileGrid(odb, pixel_shader=odb.pixel_shader, x=x, y=y)
        return image

    def create_label(
        self,
        x: int,
        y: int,
        text: str = "",
        color: str = "black",
        typeface: int = 1,
        align: str = "left",
    ) -> Label:
        """Create label object"""
        if typeface == 1:
            font = font_small
        elif typeface == 2:
            font = font_large
        else:
            raise Exception("Invalid font")
        lbl = Label(font, text=text, color=utils.colors[color], scale=1)
        lbl.anchor_point = ALIGN[align]
        lbl.anchored_position = (x, y)
        return lbl

    def create_polygon(self, points: list, color: str) -> vectorio.Polygon:
        """
        p = palette
        points = list of tuples e.g. [(1, 2), (2, 2), (3, 4), (5, 6)]
        """
        display = self.display
        polygon = vectorio.Polygon(
            pixel_shader=self.p,
            points=points,
            x=display.width // 2,
            y=display.height // 2,
            color_index=self.get_idx(color),
        )
        return polygon

    def create_bg(self, color: str) -> vectorio.Rectangle:
        """
        draw background
        """
        display = self.display
        rect = vectorio.Rectangle(
            pixel_shader=self.p,
            width=display.width + 1,
            height=display.height + 1,
            x=0,
            y=0,
            color_index=self.get_idx(color),
        )
        return rect
