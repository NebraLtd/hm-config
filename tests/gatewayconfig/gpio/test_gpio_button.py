from time import sleep
from unittest import TestCase
from unittest.mock import patch
import threading

from gatewayconfig.gpio.gpio_button import GpioButton


class MockSysfsGPIO:
    def __init__(self):
        self.value = 1


class TestMraaButton(TestCase):

    def test_button_pressed(self):
        with patch('gatewayconfig.gpio.gpio_button.SysfsGPIO', return_value=MockSysfsGPIO()):
            button = GpioButton(0, 0.2)
            button.start()
            press_count = threading.Lock()
            press_count.acquire()

            def decrement_press_count():
                press_count.release()
            button.when_held = decrement_press_count

            # When the button is pressed
            button.gpio.value = 0

            # Expect when_held to have fired
            press_count.acquire()
            self.assertTrue(press_count.locked())
            button.close()

    def test_button_never_pressed(self):
        with patch('gatewayconfig.gpio.gpio_button.SysfsGPIO', return_value=MockSysfsGPIO()):
            button = GpioButton(0, 0.2)
            button.start()
            press_count = threading.Lock()
            press_count.acquire()

            def decrement_press_count():
                press_count.release()
            button.when_held = decrement_press_count

            # After waiting longer than threshold
            sleep(0.25)

            # Expect button never pressed
            self.assertTrue(press_count.locked())
            button.close()

    def test_button_pressed_quickly(self):
        with patch('gatewayconfig.gpio.gpio_button.SysfsGPIO', return_value=MockSysfsGPIO()):
            button = GpioButton(0, 0.2)
            button.start()
            press_count = threading.Lock()
            press_count.acquire()

            def decrement_press_count():
                press_count.release()
            button.when_held = decrement_press_count

            # After pressing button but releasing before threshold
            button.gpio.value = 0
            sleep(0.075)
            button.gpio.value = 1
            sleep(0.25)

            # Expect button never pressed
            self.assertTrue(press_count.locked())
            button.close()
