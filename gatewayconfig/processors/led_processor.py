from time import sleep
from gpiozero import LED
from hm_pyhelper.hardware_definitions import is_rockpi, is_raspberry_pi
from gatewayconfig.gatewayconfig_shared_state import GatewayconfigSharedState
from gatewayconfig.logger import get_logger

LOGGER = get_logger(__name__)
LED_REFRESH_SECONDS = 2


class LEDProcessor:
    def __init__(self, status_led: LED, shared_state: GatewayconfigSharedState):
        self.status_led = status_led
        self.shared_state = shared_state

    def run(self):
        LOGGER.debug("LED LEDProcessor")

        if is_raspberry_pi() or is_rockpi():
            while True:
                # Blink fast if diagnostics are not OK
                if(not self.shared_state.are_diagnostics_ok):
                    self.status_led.blink(0.1, 0.1, 10, False)
                # Blink slow if advertising bluetooth
                elif(self.shared_state.is_advertising_bluetooth):
                    self.status_led.blink(1, 1, 1, False)
                # Solid if diagnostics are OK and not advertising
                else:
                    self.status_led.on()
                sleep(LED_REFRESH_SECONDS)
