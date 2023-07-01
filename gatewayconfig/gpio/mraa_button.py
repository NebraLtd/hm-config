from hm_pyhelper.logger import get_logger
from gatewayconfig.gpio.mraa_gpio import init_mraa_pin
from gatewayconfig.gpio.button_common import Button


LOGGER = get_logger(__name__)


class MraaButton(Button):
    """
    Unlike MraaLED, the button could not be easily monkey patched.
    Instead, basic button logic is implemented in its entirety.

    MraaButton will trigger #when_held if a button is pressed for
    hold_seconds. #when_held will only fire once if the button
    remains held down. If a button is pressed down for shorter,
    than hold_seconds, #when_held is not called.
    """

    def __init__(self, pin_number, hold_seconds):
        """
        pin_number refers to the pin number, not GPIO number:
        https://wiki.radxa.com/Rockpi4/hardware/gpio#GPIO_number
        """

        super().__init__(hold_seconds)
        LOGGER.info("Initializing mraa button on pin %s"
                    % pin_number)
        self.mraa_pin = init_mraa_pin(pin_number, False)

    def is_pressed(self):
        return self.mraa_pin.read() == 0

    def close(self):
        super().close()
        self.mraa_pin.write(0)
