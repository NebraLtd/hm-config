from time import sleep
from unittest import TestCase
from unittest.mock import patch
import threading

from gatewayconfig.gpio.mraa_button import MraaButton


class MockMraaPin():
    def __init__(self):
        self.value = 1

    def read(self):
        return self.value

    def write(self, val):
        self.value = val


class TestMraaButton(TestCase):

    @patch('gatewayconfig.gpio.mraa_button.init_mraa_pin')
    def test_button_pressed(self, init_mraa_pin_mock):
        # Given a button with .2sec press threshold
        mock_mraa_pin = MockMraaPin()
        init_mraa_pin_mock.return_value = mock_mraa_pin
        button = MraaButton(0, 0.2)
        button.start()
        press_count = threading.Lock()
        press_count.acquire()

        def decrement_press_count():
            press_count.release()
        button.when_held = decrement_press_count

        # When the button is pressed
        mock_mraa_pin.write(0)

        # Expect when_held to have fired
        press_count.acquire()
        self.assertTrue(press_count.locked())
        button.close()

    @patch('gatewayconfig.gpio.mraa_button.init_mraa_pin')
    def test_button_never_pressed(self, init_mraa_pin_mock):
        # Given a button with .2 sec press threshold
        mock_mraa_pin = MockMraaPin()
        init_mraa_pin_mock.return_value = mock_mraa_pin
        button = MraaButton(0, 0.2)
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

    @patch('gatewayconfig.gpio.mraa_button.init_mraa_pin')
    def test_button_pressed_quickly(self, init_mraa_pin_mock):
        # Given a button with .2 sec press threshold
        mock_mraa_pin = MockMraaPin()
        init_mraa_pin_mock.return_value = mock_mraa_pin
        button = MraaButton(0, 0.2)
        button.start()
        press_count = threading.Lock()
        press_count.acquire()

        def decrement_press_count():
            press_count.release()
        button.when_held = decrement_press_count

        # After pressing button but releasing before threshold
        mock_mraa_pin.write(0)
        sleep(0.075)
        mock_mraa_pin.write(1)
        sleep(0.25)

        # Expect button never pressed
        self.assertTrue(press_count.locked())
        button.close()
