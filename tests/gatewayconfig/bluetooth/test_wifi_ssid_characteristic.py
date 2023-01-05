from nmcli import DeviceWifi
from gatewayconfig.bluetooth.characteristics.wifi_ssid_characteristic import WifiSSIDCharacteristic
from gatewayconfig.gatewayconfig_shared_state import GatewayconfigSharedState
from unittest import TestCase
from unittest.mock import patch
from gatewayconfig.helpers import string_to_dbus_byte_array
from lib.cputemp.service import Service


class TestWifiSSIDCharacteristic(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Service(205, '1111', True)

    @patch('lib.nmcli_custom.device.wifi_rescan')
    @patch('lib.nmcli_custom.device.wifi',
           return_value=[
               DeviceWifi(in_use=False, ssid='TP-LINK', bssid='001122334455', mode='Infra',
                          chan=5, freq=2432, rate=54, signal=100, security='WPA1'),
               DeviceWifi(in_use=True, ssid='PHICOMM', bssid='001122334456', mode='Infra',
                          chan=1, freq=2412, rate=44, signal=96, security='WPA2')
           ])
    def test_ReadValue(self, mock1, mock2):
        characteristic = WifiSSIDCharacteristic(self.service, GatewayconfigSharedState())
        wifi_ssid = characteristic.ReadValue({})

        expected = string_to_dbus_byte_array(b'PHICOMM')
        self.assertEqual(wifi_ssid, expected)
