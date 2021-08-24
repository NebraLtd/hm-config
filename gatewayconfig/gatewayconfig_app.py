import sentry_sdk
import threading
from RPi import GPIO
from gpiozero import Button, LED

from gatewayconfig.logger import logger
from gatewayconfig.processors.bluetooth_services_processor import BluetoothServicesProcessor
from gatewayconfig.processors.led_processor import LEDProcessor
from gatewayconfig.processors.diagnostics_processor import DiagnosticsProcessor
from gatewayconfig.processors.wifi_processor import WifiProcessor
from gatewayconfig.processors.bluetooth_advertisement_processor import BluetoothAdvertisementProcessor
from gatewayconfig.gatewayconfig_shared_state import GatewayconfigSharedState
from gatewayconfig.file_loader import read_eth0_mac_address, read_wlan0_mac_address, read_miner_keys
from gatewayconfig.helpers import is_indoor_variant
import gatewayconfig.nmcli_custom as nmcli_custom

USER_BUTTON_HOLD_SECONDS = 2
INDOOR_USER_BUTTON_GPIO = 26
INDOOR_STATUS_LED_GPIO = 25

OTHER_USER_BUTTON_GPIO = 24
OTHER_STATUS_LED_GPIO = 25

class GatewayconfigApp:
    def __init__(self, sentry_dsn, balena_app_name, balena_device_uuid, variant, eth0_mac_address_filepath, wlan0_mac_address_filepath,
        miner_keys_filepath, diagnostics_json_url, ethernet_is_online_filepath, firmware_version):

        self.variant = variant
        self.init_sentry(sentry_dsn, balena_app_name, balena_device_uuid, variant)
        self.shared_state = GatewayconfigSharedState()
        self.init_nmcli()
        self.init_gpio()

        eth0_mac_address = read_eth0_mac_address(eth0_mac_address_filepath)
        wlan0_mac_address = read_wlan0_mac_address(wlan0_mac_address_filepath)
        logger.debug("Read eth0 mac address %s and wlan0 %s" % (eth0_mac_address, wlan0_mac_address))
        pub_key, onboarding_key, animal_name = read_miner_keys(miner_keys_filepath)
        logger.debug("Read onboarding pub_key: %s + animal_name: %s" % (pub_key, animal_name))

        self.bluetooth_services_processor = BluetoothServicesProcessor(eth0_mac_address, wlan0_mac_address, onboarding_key, pub_key, firmware_version, ethernet_is_online_filepath, self.shared_state)
        self.led_processor = LEDProcessor(self.status_led, self.shared_state)
        self.diagnostics_processor = DiagnosticsProcessor(diagnostics_json_url, self.shared_state)
        self.wifi_processor = WifiProcessor(self.shared_state)
        self.bluetooth_advertisement_processor = BluetoothAdvertisementProcessor(eth0_mac_address, self.shared_state)
        
    def start(self):
        logger.debug("Starting ConfigApp")
        try:
            self.start_threads()

        except KeyboardInterrupt:
            logger.debug("KEYBOAD INTERRUPTION")
            self.stop()

        except Exception:
            logger.exception('GatewayConfigApp failed for unknown reason')
            self.stop()

    def stop(self):
        logger.debug("Stopping ConfigApp")
        GPIO.cleanup()
        # Quits the cputemp application
        self.bluetooth_processor.quit()

    def init_sentry(self, sentry_dsn, balena_app_name, balena_device_uuid, variant):
        sentry_sdk.init(sentry_dsn, environment=balena_app_name)
        sentry_sdk.set_user({ "id": balena_device_uuid })
        sentry_sdk.set_context("variant", { variant })

    def init_nmcli(self):
        nmcli_custom.disable_use_sudo()

    def init_gpio(self):
        if is_indoor_variant(self.variant):
            user_button_gpio = INDOOR_USER_BUTTON_GPIO
            status_led_gpio = INDOOR_STATUS_LED_GPIO
        else:
            user_button_gpio = OTHER_USER_BUTTON_GPIO
            status_led_gpio = OTHER_STATUS_LED_GPIO
        
        self.user_button = Button(user_button_gpio, hold_time=USER_BUTTON_HOLD_SECONDS)
        self.user_button.when_held= self.start_bluetooth_advertisement
        self.status_led = LED(status_led_gpio)

    # Use daemon threads so that everything exists cleanly when the program stops
    def start_threads(self):
        self.bluetooth_services_thread = threading.Thread(target=self.bluetooth_services_processor.run)
        self.led_thread = threading.Thread(target=self.led_processor.run)
        self.diagnostics_thread = threading.Thread(target=self.diagnostics_processor.run)
        self.wifi_thread = threading.Thread(target=self.wifi_processor.run)
        self.bluetooth_advertisement_thread = threading.Thread(target=self.bluetooth_advertisement_processor.run)

        self.led_thread.daemon = True
        self.led_thread.start()

        # self.bluetooth_services_thread.daemon = True
        self.bluetooth_services_thread.start()

        # self.diagnostics_thread.daemon = True
        self.diagnostics_thread.start()

        # self.wifi_thread.daemon = True
        self.wifi_thread.start()

        # self.bluetooth_advertisement_thread.daemon = True
        self.bluetooth_advertisement_thread.start()

    def start_bluetooth_advertisement(self):
        logger.debug("Starting bluetooth advertisement")
        self.shared_state.should_advertise_bluetooth = True