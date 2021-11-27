import time
import threading

from hm_pyhelper.logger import get_logger
from gatewayconfig.gpio.mraa_gpio import init_mraa_pin


LOGGER = get_logger(__name__)


# How often to check for button presses
MONITOR_CHECK_INTERVAL_SECONDS = 0.05


class MraaButton(threading.Thread):
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

        super(MraaButton, self).__init__()
        LOGGER.info("Initializing mraa button on pin %s"
                    % pin_number)
        self.daemon = True
        self.cancelled = False
        self.mraa_pin = init_mraa_pin(pin_number, False)
        self.hold_seconds = hold_seconds
        self.when_held = None
        self.reset_pressed_state()

    def run(self):
        while not self.cancelled:
            if not self.is_pressed():
                self.reset_pressed_state()
            else:
                self.process_press()

            time.sleep(MONITOR_CHECK_INTERVAL_SECONDS)

    def process_press(self):
        """
        If this is the first time this press has been detected,
        record the time for future reference. If the press has
        already been detected, attempt to trigger #when_held.
        """

        if self.last_pressed_at is None:
            LOGGER.debug("Button pressed for first time")
            self.last_pressed_at = time.time()
        else:
            self.trigger_when_held_after_hold_seconds()

    def trigger_when_held_after_hold_seconds(self):
        """
        If #when_held has not been invoked due to this press,
        and it is defined, invoke it.
        """

        if self.when_held and not self.is_press_already_registered:
            if self.have_hold_seconds_elapsed():
                LOGGER.debug("Button pressed down for "
                             "`hold_seconds` (%s secs)"
                             % self.hold_seconds)
                self.is_press_already_registered = True
                self.when_held()

    def have_hold_seconds_elapsed(self):
        elapsed_seconds = time.time() - self.last_pressed_at
        return elapsed_seconds >= self.hold_seconds

    def is_pressed(self):
        return self.mraa_pin.read() == 0

    def reset_pressed_state(self):
        self.last_pressed_at = None
        self.is_press_already_registered = False

    def close(self):
        self.cancelled = True
        self.mraa_pin.write(0)
