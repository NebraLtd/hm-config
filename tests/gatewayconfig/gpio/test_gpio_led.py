from unittest import TestCase
from unittest.mock import call, patch

from gatewayconfig.gpio import gpio_led


class TestGpioLED(TestCase):

    @patch('gatewayconfig.gpio.gpio_led.SysfsGPIO')
    def test_init(self, sysfs_gpio_mock):
        """Should create and initialize a `SysfsGPIO` instance with supplied `pin_number` param.
        """

        led = gpio_led.GpioLED(
            pin_number=3,
            active_high=True,
            initial_value=False,
        )

        sysfs_gpio_mock.assert_called_with(3)
        assert led.gpio.export is True
        assert led.gpio.direction == 'out'
        assert led.gpio.active_low is False
        assert led.gpio.value == 0

    @patch('gatewayconfig.gpio.gpio_led.SysfsGPIO')
    def test_write(self, sysfs_gpio_mock):
        """Should set the `gpio.value` to corresponding given value converted to `int`.
        """

        led = gpio_led.GpioLED(
            pin_number=3,
            active_high=True,
            initial_value=False,
        )

        led._write(True)
        assert led.gpio.value == 1

        led._write(False)
        assert led.gpio.value == 0
