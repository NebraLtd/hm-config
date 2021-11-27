import os
from unittest import TestCase
from unittest.mock import patch, mock_open

from gpiozero import Device
from gpiozero.pins.mock import MockFactory

from gatewayconfig.gatewayconfig_app import GatewayconfigApp

Device.pin_factory = MockFactory()

ETHO_FILE_MOCK = 'A1:B2:C3:DD:E5:F6'
DIAGNOSTICS_RESPONSE_MOCK = (
    '{"AN":"big-apple-animal","APPNAME":"Outdoor","BA":"HELIUM-OUTDOOR-915","BCH":0005594,"BN":"warm-night",'
    '"BSP":0.0,"BT":true,"BUTTON":24,"CELLULAR":true,"E0":"00:00:00:EF:7F:F7","ECC":true,"ECCOB":true,"FR":"915",'
    '"FRIENDLY":"Nebra Outdoor Hotspot Gen 1","FW":"2021.10.07.1","ID":"111111111111439dbbdb408ca51a93f6",'
    '"LOR":true,"LTE":false,"MAC":"eth0","MC":true,"MD":true,"MH":1,"MN":"none","MR":false,"MS":false,'
    '"OK":"11111111111111zFs11TjTSb2hPBZMwq527XdQv2L7ibh4Ma4f4D","PF":true,'
    '"PK":"11111111111111zFs11TjTSb2hPBZMwq527XdQv2L7ibh4Ma4f4D","RE":"UN123","RESET":38,"RPI":"00000000000092f3",'
    '"SPIBUS":"spidev1.2","STATUS":25,"TYPE":"Full","VA":"NEBHNT-OUT1","W0":"00:00:6B:20:00:42",'
    '"last_updated":"17:40 UTC 15 Oct 2021"}')


class TestGatewayconfigApp(TestCase):

    @patch('lib.cputemp.bletools.BleTools.get_bus')
    @patch('lib.cputemp.bletools.BleTools.find_adapter')
    @patch('dbus.Interface')
    @patch('builtins.open', new_callable=mock_open, read_data=ETHO_FILE_MOCK)
    @patch('requests.get', response=DIAGNOSTICS_RESPONSE_MOCK)
    @patch('gatewayconfig.gpio.mraa_button.init_mraa_pin')
    def test_gpio_pins(self, mock_dbus_interface, mock_findadapter, mock_getbus,
                       mock_file, mock_diagnostics, mock_mraa_pin):
        os.environ['BALENA_DEVICE_TYPE'] = 'raspberrypi3-64'
        app = GatewayconfigApp('https://11111111111111119f8b0c9b118c415a@o111111.ingest.sentry.io/1111111',
                               'BALENA_APP_NAME', 'BALENA_DEVICE_UUID',
                               'NEBHNT-IN1', 'ETH0_MOCK_USED',
                               'WLAN0_MAC_ADDRESS_FILEPATH',
                               'DIAGNOSTICS_JSON_URL',
                               'ETHERNET_IS_ONLINE_FILEPATH',
                               'FIRMWARE_VERSION')

        self.assertEqual(app.variant, 'NEBHNT-IN1')
        self.assertEqual(app.get_button_gpio(), 26)
        self.assertEqual(app.get_status_led_gpio(), 25)
        app.stop()
