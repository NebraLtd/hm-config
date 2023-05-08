from unittest import TestCase
from unittest.mock import call, patch

from gatewayconfig.gpio.neopixel_led import (
    NeopixelLED, LED_FREQ_HZ, LED_BRIGHTNESS, LED_COLOR_DEFAULT, LED_COLOR_OFF, Color
)


class TestNeopixelLED(TestCase):

    @patch('gatewayconfig.gpio.neopixel_led.PixelStrip')
    def test_init(self, pixel_strip_mock):
        """Should create and initialize a `NeopixelLED` instance with supplied `PixelStrip` params.
        """

        neopixel_led = NeopixelLED(
            led_count=4,
            dma=1,
            channel=2,
            pin_number=3,
            active_high=True,
        )

        pixel_strip_mock.assert_called_with(4, 3, LED_FREQ_HZ, 1, False,  LED_BRIGHTNESS, 2)
        pixel_strip_mock.return_value.begin.assert_called()
        assert neopixel_led.strip is pixel_strip_mock.return_value

    @patch('gatewayconfig.gpio.neopixel_led.PixelStrip')
    def test_write_true(self, pixel_strip_mock):
        """Should call `setPixelColor` and `show` methods on the `PixelStrip` instance,
        with the corresponding DEFAULT color.
        """

        neopixel_led = NeopixelLED(
            led_count=4,
            dma=1,
            channel=2,
            pin_number=5,
            active_high=True,
        )
        neopixel_led.strip.numPixels.return_value = 4
        neopixel_led._write(True)
        neopixel_led.strip.setPixelColor.assert_has_calls(
            [call(led_no, Color(*LED_COLOR_DEFAULT)) for led_no in range(4)]
        )
        neopixel_led.strip.show.assert_called_once()

    @patch('gatewayconfig.gpio.neopixel_led.PixelStrip')
    def test_write_false(self, pixel_strip_mock):
        """Should call `setPixelColor` and `show` methods on the `PixelStrip` instance,
        with the corresponding OFF color.
        """

        neopixel_led = NeopixelLED(
            led_count=4,
            dma=1,
            channel=2,
            pin_number=6,
            active_high=True,
        )
        neopixel_led.strip.numPixels.return_value = 4
        neopixel_led._write(False)
        neopixel_led.strip.setPixelColor.assert_has_calls(
            [call(led_no, Color(*LED_COLOR_OFF)) for led_no in range(4)]
        )
        neopixel_led.strip.show.assert_called_once()
