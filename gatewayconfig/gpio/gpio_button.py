from gpio4 import SysfsGPIO

from hm_pyhelper.logger import get_logger
from gatewayconfig.gpio.button_common import Button


LOGGER = get_logger(__name__)


class GpioButton(Button):
    def __init__(self, pin_number, hold_seconds):
        super().__init__(hold_seconds)
        LOGGER.info("Initializing GPIO button on pin %s" % pin_number)
        self.gpio = SysfsGPIO(pin_number)
        self.gpio.export = True
        self.gpio.direction = 'in'

    def is_pressed(self):
        return self.gpio.value == 0

    def close(self):
        super().close()
        self.gpio.export = False
