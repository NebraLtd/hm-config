from gpiozero import LED
from gpiozero.pins.mock import MockFactory

from rpi_ws281x import PixelStrip, Color

from hm_pyhelper.logger import get_logger


LOGGER = get_logger(__name__)

LED_FREQ_HZ = 800000
LED_BRIGHTNESS = 255
LED_COLOR_DEFAULT = (0, 255, 0)
LED_COLOR_OFF = (0, 0, 0)


class NeopixelLED(LED):
    """
    Extend gpiozero.LED and override the write method to interact with rpi-ws281x LED strip lib.
    """

    def __init__(
        self,
        led_count: int,
        dma: int,
        channel: int,
        pin_number=None,
        *,
        active_high=True,
        initial_value=False,
    ):
        super().__init__(pin_number, active_high=active_high,
                         initial_value=initial_value, pin_factory=MockFactory())

        LOGGER.info(
            "Initializing Neopixel LED on pin %s, dma %s, channel %s",
            pin_number, dma, channel
        )

        self.strip = PixelStrip(
            led_count, pin_number, LED_FREQ_HZ, dma, not active_high, LED_BRIGHTNESS, channel
        )
        self.strip.begin()

    def _write(self, value):
        color = Color(*LED_COLOR_DEFAULT) if value else Color(*LED_COLOR_OFF)
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)

        self.strip.show()
