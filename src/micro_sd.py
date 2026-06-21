import sdcardio
import storage


class MicroSD:
    def __init__(self, spi, cs):
        try:
            self.sdcard = sdcardio.SDCard(spi, cs)
            self.vfs = storage.VfsFat(self.sdcard)
            storage.mount(self.vfs, "/sd")
            self.mounted = True
        except OSError:
            self.mounted = False

    def write_to_file(self, filename: str, text: str) -> None:
        with open("/sd/" + filename + ".txt", "w") as f:
            f.write(text + "\r\n")
