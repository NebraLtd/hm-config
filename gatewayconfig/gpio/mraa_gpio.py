import subprocess  # nosec
from hm_pyhelper.logger import get_logger

LOGGER = get_logger(__name__)

try:
    import mraa
except Exception:
    LOGGER.warn("mraa not loaded. If you see this message outside of unit "
                "tests, this may cause a problem.")


def init_mraa_pin(pin_number, is_input):
    """
    Instantiate a new mraa.Gpio instance on `pin`.
    Pull the pin high before returning.
    Defining this method outside MraaButton
    so that it is easier to mock from tests.
    """

    mraa_pin = mraa.Gpio(pin_number)
    if is_input:
        mraa_dir = mraa.DIR_IN
    else:
        mraa_dir = mraa.DIR_OUT

    mraa_pin.dir(mraa_dir)
    # pull up before usage
    mraa_gpio_write(pin_number, 1)
    return mraa_pin


def mraa_gpio_write(pin_number, val):
    """
    Some aspect of initialization prevents mraa.Gpio.write
    from having any effect. It is necessary to pull-up the
    GPIO before using it but this is not possible using the
    mraa Python library. In fact similar behavior is
    observed interacting with the filesystem directly.

    ```
    # echo 154 > /sys/class/gpio/export
    # echo 1 > /sys/class/gpio/gpio154/value
    bash: echo: write error: Operation not permitted
    ```

    Using `mraa-gpio set PIN 1` solves the issue. After
    invoking that command, the GPIO is then writable
    normally.

    This logic cannot be easily added to
    start-gateway-config.sh because it would need to
    include logic that replicates pyhelper methods
    like is_raspberry_pi and hardware_definitions.
    """

    subprocess.check_call(['mraa-gpio', 'set', str(pin_number), str(val)])  # nosec NOSONAR
