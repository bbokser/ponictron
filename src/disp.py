import utils

# import gc  # garbage collector
# print('free memory left before (most) imports: ', gc.mem_free())
# from ulab import numpy as np
import displayio
import vectorio
from fourwire import FourWire
import adafruit_ili9341
import supervisor
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.bitmap_label import Label
from font_ostrich_sans_black_24 import FONT as font_small
from font_ostrich_sans_black_60 import FONT as font_large

# print('free memory left after imports: ', gc.mem_free())

supervisor.runtime.autoreload = False

displayio.release_displays()


class Disp:
    def __init__(self, spi, cs, dc, reset):

        # epd_busy = board.GP16
        display_bus = FourWire(
            spi, command=dc, chip_select=cs, reset=reset, baudrate=1000000
        )
        display = adafruit_ili9341.ILI9341(
            display_bus, width=320, height=240, rotation=180
        )

        # create displayio group
        g = displayio.Group()

        # create palette
        color_list = list(utils.colors.values())
        self.color_names = list(utils.colors.keys())
        n = len(color_list)
        p = displayio.Palette(n)
        for i in range(0, n):
            p[i] = color_list[i]

        self.display = display
        self.width = display.width
        self.height = display.height
        self.g = g
        self.p = p

        self.color_list = color_list
        # change this to match the smaller font size
        self.size_font_small = 24
        # TODO: implement brightness
        self.brightness = 1

    def clear(self) -> None:
        # clear the group
        self.g = displayio.Group()

    def update(self) -> None:
        # Add the Group to the Display
        self.display.root_group = self.g
        self.display.refresh()

    def get_idx(self, color: str) -> int:
        """
        Convert color name to index
        """
        return self.color_names.index(color)

    def draw_bmp(self, path: str, x: int, y: int) -> None:
        odb = displayio.OnDiskBitmap(path)
        image = displayio.TileGrid(odb, pixel_shader=odb.pixel_shader, x=x, y=y)
        self.g.append(image)

    def draw_text(
        self, text: str, x: int, y: int, color: str = "black", opt: int = 1
    ) -> None:
        # display = self.display
        # lbl = Label(terminalio.FONT, text=text, color=utils.colors[color], scale=scale)
        if opt == 1:
            font = font_small
        elif opt == 2:
            font = font_large
        else:
            raise Exception("Invalid font")
        lbl = Label(font, text=text, color=utils.colors[color], scale=1)
        lbl.anchor_point = (0.0, 1.0)
        lbl.anchored_position = (x, y)  # (display.width // 2, display.height // 2)
        self.g.append(lbl)
        return None

    def set_colon_off(self) -> None:
        pass

    def set_colon_on(self) -> None:
        pass

    def display_int(self, year: int) -> None:
        pass

    def wink_left(self, wink_bool: bool) -> None:
        pass

    def wink_right(self, wink_bool: bool) -> None:
        pass

    def display_hourmin(self, month: int, day: int) -> None:
        pass

    def display_wday_set(self, wday_set, blink_pos: int, blink_bool: bool) -> None:
        pass

    def display_letter(self, letter: str) -> None:
        pass

    def display_24hr(self) -> None:
        pass

    def display_12hr(self) -> None:
        pass

    def apply_info(self, info: dict) -> None:
        display = self.display
        self.draw_bg(color="white")
        x_center = display.width // 2

        col_1 = 5
        col_2 = x_center + int(x_center / 4)
        row_1 = self.size_font_small - 6
        row_step_size = self.size_font_small
        row_2 = row_1 + row_step_size
        row_3 = row_2 + row_step_size
        row_4 = row_3 + row_step_size
        row_5 = row_4 + row_step_size
        offset_icon = 18
        offset_txt = 24

        self.draw_text(
            text=info["weekday"], x=col_1, y=14 + self.size_font_small, opt=2
        )
        self.draw_text(text=info["meridiem"], x=int(3 * x_center / 4), y=row_2)
        self.draw_text(
            text=info["month"] + " " + info["day"] + " " + info["year"],
            x=col_1,
            y=row_3,
        )
        self.draw_bmp("/bmps/temp.bmp", x=col_1, y=row_4 - offset_icon)
        self.draw_text(
            text=info["probe_0_temp"],
            x=col_1 + offset_txt,
            y=row_4,
        )

        self.draw_bmp("/bmps/elec.bmp", x=col_2, y=row_1 - offset_icon)

        self.draw_bmp("/bmps/temp.bmp", x=col_2, y=row_2 - offset_icon)
        self.draw_text(text=info["temp"], x=col_2 + offset_txt, y=row_2)

        self.draw_bmp("/bmps/humidity.bmp", x=col_2, y=row_3 - offset_icon)
        self.draw_text(text=info["humidity"] + " %", x=col_2 + offset_txt, y=row_3)

        self.draw_bmp("/bmps/elec.bmp", x=col_1, y=row_5 - offset_icon)
        self.draw_text(
            text=info["lightinfo"],
            x=col_1 + offset_txt,
            y=row_5,
        )
        return None

    def draw_polygon(self, points: list, color: str) -> None:
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
        self.g.append(polygon)
        return None

    def draw_bg(self, color: str) -> None:
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
        self.g.append(rect)
        return None
