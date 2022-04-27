from nmcli import Connection
from gatewayconfig.bluetooth.characteristics.wifi_configured_services_characteristic import \
    WifiConfiguredServicesCharacteristic
from gatewayconfig.gatewayconfig_shared_state import GatewayconfigSharedState
from unittest import TestCase
from unittest.mock import patch
from gatewayconfig.helpers import string_to_dbus_byte_array
from lib.cputemp.service import Service


class TestWifiConfiguredServicesCharacteristic(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Service(201, '1111', True)

    @patch('lib.nmcli_custom.connection',
           return_value=[
               Connection(name='supervisor0', uuid='00000005-0006-0007-0008-000000000009',
                          conn_type='bridge', device='supervisor0'),
               Connection(name='TP-LINK', uuid='00000001-0002-0003-0004-000000000005',
                          conn_type='wifi', device='wlan0'),
               Connection(name='Wired connection 1', uuid='0000000a-000b-000c-000d-00000000000e',
                          conn_type='ethernet', device='eth0')

           ])
    def test_ReadValue(self, mock1):
        characteristic = WifiConfiguredServicesCharacteristic(
            self.service,
            GatewayconfigSharedState())
        wifi_configured_services = characteristic.ReadValue({})

        expected = string_to_dbus_byte_array(b'\n\x07TP-LINK')
        self.assertEqual(wifi_configured_services, expected)
