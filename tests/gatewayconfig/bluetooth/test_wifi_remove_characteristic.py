from gatewayconfig.bluetooth.characteristics.wifi_remove_characteristic import \
    WifiRemoveCharacteristic
from unittest import TestCase
from unittest.mock import patch
from gatewayconfig.helpers import string_to_dbus_byte_array
from lib.cputemp.service import Service


class TestWifiRemoveCharacteristic(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Service(203, '1111', True)

    @patch('lib.nmcli_custom.connection.delete')
    def test_WriteValue(self, mock1):
        try:
            with self.assertLogs(
                    'gatewayconfig.bluetooth.characteristics.wifi_remove_characteristic',
                    level='DEBUG') as cm:
                characteristic = WifiRemoveCharacteristic(self.service)
                characteristic.WriteValue(string_to_dbus_byte_array(b'\n\x07TP-LINK'), {})

                self.assertEqual(len(cm.output), 2)
                self.assertIn('Write WiFi Remove', cm.output[0])
                self.assertIn('Connection TP-LINK should be deleted', cm.output[1])
        except Exception as e:
            self.fail("Unexpected exception while testing WifiRemoveCharacteristic: %s" % str(e))
