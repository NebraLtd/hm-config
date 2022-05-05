import dbus

from gatewayconfig.bluetooth.characteristics.wifi_connect_characteristic import \
    WifiConnectCharacteristic
from unittest import TestCase
from unittest.mock import patch
from gatewayconfig.helpers import string_to_dbus_byte_array
from lib.cputemp.service import Service


class TestWifiConnectCharacteristic(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Service(202, '1111', True)

    @patch('gatewayconfig.bluetooth.characteristics.wifi_connect_characteristic.CommandThread')
    def test_WriteValue(self, mock1):
        try:
            with self.assertLogs(
                    'gatewayconfig.bluetooth.characteristics',
                    level='DEBUG') as cm:
                characteristic = WifiConnectCharacteristic(self.service)
                characteristic.WriteValue(
                    dbus.Array(string_to_dbus_byte_array(b'\n\fTP-LINK_4672\x12\t123456789'),
                               signature='y'), {})

                self.assertGreaterEqual(len(cm.output), 2)
                self.assertIn('Write WiFi Connect', cm.output[0])
                self.assertIn('Connecting to TP-LINK_4672 is started', cm.output[1])
        except Exception as e:
            self.fail("Unexpected exception while testing WifiRemoveCharacteristic: %s" % str(e))
