from unittest import TestCase
from unittest.mock import patch, mock_open

from gpiozero import Device
from gpiozero.pins.mock import MockFactory

from gatewayconfig.gatewayconfig_app import GatewayconfigApp
import gatewayconfig.constants as constants

Device.pin_factory = MockFactory()

ETHO_FILE_MOCK = 'A1:B2:C3:DD:E5:F6'

class TestGatewayconfigSha(TestCase):

    @patch('lib.cputemp.bletools.BleTools.get_bus')
    @patch('lib.cputemp.bletools.BleTools.find_adapter')
    @patch('dbus.Interface')
    @patch('builtins.open', new_callable=mock_open, read_data=ETHO_FILE_MOCK)
    def test_gpio_pins(self, mock_dbus_interface, mock_findadapter, mock_getbus, mock_file):
        app = GatewayconfigApp('https://11111111111111119f8b0c9b118c415a@o111111.ingest.sentry.io/1111111', 'BALENA_APP_NAME', 'BALENA_DEVICE_UUID', 'NEBHNT-IN1',
        'ETH0_MOCK_USED', 'WLAN0_MAC_ADDRESS_FILEPATH', 'MINER_KEYS_FILEPATH', 'DIAGNOSTICS_JSON_URL', 'ETHERNET_IS_ONLINE_FILEPATH', 'FIRMWARE_VERSION')

        self.assertEqual(app.variant, 'NEBHNT-IN1')
        self.assertEqual(app.get_button_pin(), 26)
        self.assertEqual(app.get_status_led_pin(), 25)
        app.stop()
