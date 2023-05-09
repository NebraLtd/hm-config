import sentry_sdk
import threading
import requests
from gpiozero import Button, LED

from hm_pyhelper.hardware_definitions import is_rockpi, is_raspberry_pi, \
                                             variant_definitions

from gatewayconfig.logger import get_logger
from gatewayconfig.processors.bluetooth_services_processor import BluetoothServicesProcessor
from gatewayconfig.processors.led_processor import LEDProcessor
from gatewayconfig.processors.diagnostics_processor import DiagnosticsProcessor
from gatewayconfig.processors.bluetooth_advertisement_processor import BluetoothAdvertisementProcessor
from gatewayconfig.gatewayconfig_shared_state import GatewayconfigSharedState
from gatewayconfig.file_loader import read_eth0_mac_address, read_wlan0_mac_address
from gatewayconfig.gpio.mraa_button import MraaButton
from gatewayconfig.gpio.mraa_led import MraaLED
from gatewayconfig.gpio.neopixel_led import NeopixelLED
import lib.nmcli_custom as nmcli_custom


USER_BUTTON_HOLD_SECONDS = 2
LOGGER = get_logger(__name__)


class GatewayconfigApp:
    def __init__(self, sentry_dsn, balena_app_name, balena_device_uuid, variant, eth0_mac_address_filepath,
                 wlan0_mac_address_filepath, diagnostics_json_url, ethernet_is_online_filepath,
                 firmware_version
                 ):

        self.variant = variant
        self.variant_details = variant_definitions[variant]
        self.init_sentry(
            sentry_dsn=sentry_dsn,
            release=firmware_version,
            balena_id=balena_device_uuid,
            balena_app=balena_app_name,
            variant=variant)
        self.shared_state = GatewayconfigSharedState()
        self.init_nmcli()
        self.user_button = None
        self.status_led = None
        self.init_gpio(variant)

        eth0_mac_address = read_eth0_mac_address(eth0_mac_address_filepath)
        wlan0_mac_address = read_wlan0_mac_address(wlan0_mac_address_filepath)
        LOGGER.debug("Read eth0 mac address {} and wlan0 {}".format(eth0_mac_address, wlan0_mac_address))
        self.shared_state.load_public_key()

        self.bluetooth_services_processor = BluetoothServicesProcessor(
                eth0_mac_address, wlan0_mac_address,
                firmware_version, ethernet_is_online_filepath,
                self.shared_state
        )

        if self.status_led is not None:
            self.led_processor = LEDProcessor(self.status_led, self.shared_state)
        self.diagnostics_processor = DiagnosticsProcessor(
                diagnostics_json_url,
                self.shared_state
        )
        self.bluetooth_advertisement_processor = BluetoothAdvertisementProcessor(
                eth0_mac_address,
                self.shared_state,
                self.variant_details
        )

    def start(self):
        LOGGER.debug("Starting ConfigApp")
        try:
            self.start_threads()

        except KeyboardInterrupt:
            LOGGER.debug("KEYBOAD INTERRUPTION")
            self.stop()

        except Exception:
            LOGGER.exception('GatewayConfigApp failed for unknown reason')
            self.stop()

    def stop(self):
        LOGGER.debug("Stopping ConfigApp")
        if self.user_button is not None:
            self.user_button.close()
        if self.status_led is not None:
            self.status_led.close()
        # Quits the cputemp application
        self.bluetooth_services_processor.quit()

    def init_sentry(self, sentry_dsn, release, balena_id, balena_app, variant):
        """
        Initialize sentry with balena_id and balena_app as tag.
        If sentry_dsn is not set, do nothing.
        """

        if not sentry_dsn:
            return

        sentry_sdk.init(
            sentry_dsn,
            release=f"hm-config@{release}"
        )

        sentry_sdk.set_context("variant", {variant})

        sentry_sdk.set_tag("balena_id", balena_id)
        sentry_sdk.set_tag("balena_app", balena_app)

    def init_nmcli(self):
        nmcli_custom.disable_use_sudo()

    def check_password_reset(self):
        try:
            resp = requests.post(
                'http://diagnostics/password_reset',
                timeout=5
            )
            password_reset_data = resp.json()
            return password_reset_data.get('password_updated')
        except Exception:
            return False

    def button_held(self):
        if not self.check_password_reset():
            self.start_bluetooth_advertisement()

    def init_gpio(self, variant):
        """
        This code was originally written for Raspberry Pi but ROCK Pi does not
        support gpiozero. Custom GPIO implementations for ROCK Pi are used based
        on the detected hardware.
        """
        if is_raspberry_pi():
            btn = self.get_button_gpio()
            if btn is not None:
                self.user_button = Button(btn, hold_time=USER_BUTTON_HOLD_SECONDS)
            led = self.get_status_led_gpio()
            if led is not None:
                self.status_led = LED(led)
            else:
                neopixel_params = self.get_status_neopixel()
                if neopixel_params is not None:
                    self.status_led = NeopixelLED(
                        led_count=neopixel_params['LED_COUNT'],
                        pin_number=neopixel_params['PIN'],
                        dma=neopixel_params['DMA'],
                        channel=neopixel_params['CHANNEL'],
                        active_high=neopixel_params['ACTIVE_HIGH'],
                    )
        elif is_rockpi():
            btn = self.get_button_pin()
            if btn is not None:
                self.user_button = MraaButton(btn, hold_seconds=USER_BUTTON_HOLD_SECONDS)
                self.user_button.start()
            led = self.get_status_led_pin()
            if led is not None:
                self.status_led = MraaLED(led)
        else:
            LOGGER.warn("LEDs and buttons are disabled. "
                        "GPIO not yet supported on this device: %s"
                        % variant)

        if self.user_button is not None:
            self.user_button.when_held = self.button_held

    # Use daemon threads so that everything exists cleanly when the program stops
    def start_threads(self):
        self.bluetooth_services_thread = threading.Thread(target=self.bluetooth_services_processor.run)
        if self.status_led is not None:
            self.led_thread = threading.Thread(target=self.led_processor.run)
        self.diagnostics_thread = threading.Thread(target=self.diagnostics_processor.run)
        self.bluetooth_advertisement_thread = threading.Thread(target=self.bluetooth_advertisement_processor.run)

        if self.status_led is not None:
            self.led_thread.daemon = True
            self.led_thread.start()

        # self.bluetooth_services_thread.daemon = True
        self.bluetooth_services_thread.start()

        # self.diagnostics_thread.daemon = True
        self.diagnostics_thread.start()

        # self.bluetooth_advertisement_thread.daemon = True
        self.bluetooth_advertisement_thread.start()

    def start_bluetooth_advertisement(self):
        LOGGER.debug("Starting bluetooth advertisement")
        self.shared_state.should_advertise_bluetooth_condition_event.set()
        self.shared_state.run_fast_diagnostic_condition_event.set()

    def get_button_gpio(self):
        return self.variant_details.get('BUTTON')

    def get_status_led_gpio(self):
        return self.variant_details.get('STATUS')

    def get_button_pin(self):
        return self.variant_details.get('GPIO_PIN_BUTTON')

    def get_status_led_pin(self):
        return self.variant_details.get('GPIO_PIN_LED')

    def get_status_neopixel(self):
        return self.variant_details.get('STATUS_NEOPIXEL')
