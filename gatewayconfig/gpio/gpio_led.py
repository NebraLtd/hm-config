from gpio4 import SysfsGPIO

from gpiozero import LED
from gpiozero.pins.mock import MockFactory

from hm_pyhelper.logger import get_logger

LOGGER = get_logger(__name__)


class GpioLED(LED):
    """
    Extend gpiozero.LED and override the write method to simply use a gpio.
    """

    def __init__(self, pin_number=None, *, active_high=True, initial_value=False):
        super().__init__(pin_number, active_high=active_high,
                         initial_value=initial_value, pin_factory=MockFactory())

        LOGGER.info("Initializing GPIO LED on pin %s" % pin_number)

        self.gpio = SysfsGPIO(pin_number)
        self.gpio.export = True
        self.gpio.direction = 'out'
        self.gpio.active_low = not active_high
        self.gpio.value = int(initial_value)

    def _write(self, value):
        self.gpio.value = int(value)
