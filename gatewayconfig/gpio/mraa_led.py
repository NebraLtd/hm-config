from gpiozero import LED
from gpiozero.pins.mock import MockFactory

from hm_pyhelper.logger import get_logger
from gatewayconfig.gpio.mraa_gpio import init_mraa_pin

LOGGER = get_logger(__name__)


class MraaLED(LED):
    """"
    Extend gpiozero.LED and override the write method to interact with libmraa.
    """

    def __init__(self, pin_number=None, *, active_high=True, initial_value=False):
        super().__init__(pin_number, active_high=active_high,
                         initial_value=initial_value, pin_factory=MockFactory())

        LOGGER.info("Initializing mraa LED on pin %s"
                    % pin_number)

        self.mraa_pin = init_mraa_pin(pin_number, True)

    def _write(self, value):
        self.mraa_pin.write(value)
