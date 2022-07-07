import sentry_sdk
import threading
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
            balena_app=balena_app_name)
        self.shared_state = GatewayconfigSharedState()
        self.init_nmcli()
        self.init_gpio(variant)

        eth0_mac_address = read_eth0_mac_address(eth0_mac_address_filepath)
        wlan0_mac_address = read_wlan0_mac_address(wlan0_mac_address_filepath)
        LOGGER.debug("Read eth0 mac address %s and wlan0 %s" % (eth0_mac_address, wlan0_mac_address))
        self.shared_state.load_public_key()

        self.bluetooth_services_processor = BluetoothServicesProcessor(
                eth0_mac_address, wlan0_mac_address,
                firmware_version, ethernet_is_online_filepath,
                self.shared_state
        )
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
        self.user_button.close()
        self.status_led.close()
        # Quits the cputemp application
        self.bluetooth_services_processor.quit()

    def init_sentry(self, sentry_dsn, release, balena_id, balena_app):
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

        sentry_sdk.set_tag("balena_id", balena_id)
        sentry_sdk.set_tag("balena_app", balena_app)

    def init_nmcli(self):
        nmcli_custom.disable_use_sudo()

    def init_gpio(self, variant):
        """
        This code was originally written for Raspberry Pi but ROCK Pi does not
        support gpiozero. Custom GPIO implementations for ROCK Pi are used based
        on the detected hardware.
        """
        if is_raspberry_pi():
            self.user_button = Button(self.get_button_gpio(), hold_time=USER_BUTTON_HOLD_SECONDS)
            self.status_led = LED(self.get_status_led_gpio())
        elif is_rockpi():
            self.user_button = MraaButton(self.get_button_pin(), hold_seconds=USER_BUTTON_HOLD_SECONDS)
            self.user_button.start()
            self.status_led = MraaLED(self.get_status_led_pin())
        else:
            LOGGER.warn("LEDs and buttons are disabled. "
                        "GPIO not yet supported on this device: %s"
                        % variant)

        self.user_button.when_held = self.start_bluetooth_advertisement

    # Use daemon threads so that everything exists cleanly when the program stops
    def start_threads(self):
        self.bluetooth_services_thread = threading.Thread(target=self.bluetooth_services_processor.run)
        self.led_thread = threading.Thread(target=self.led_processor.run)
        self.diagnostics_thread = threading.Thread(target=self.diagnostics_processor.run)
        self.bluetooth_advertisement_thread = threading.Thread(target=self.bluetooth_advertisement_processor.run)

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

    def get_button_gpio(self):
        return self.variant_details['BUTTON']

    def get_status_led_gpio(self):
        return self.variant_details['STATUS']

    def get_button_pin(self):
        return self.variant_details['GPIO_PIN_BUTTON']

    def get_status_led_pin(self):
        return self.variant_details['GPIO_PIN_LED']
