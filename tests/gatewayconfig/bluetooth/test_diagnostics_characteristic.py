from lib.cputemp.service import Service
from unittest import TestCase
from unittest.mock import patch, Mock
from gatewayconfig.bluetooth.characteristics.diagnostics_characteristic \
    import DiagnosticsCharacteristic

# Should correspond with BluetoothConnectionAdvertisement.ADVERTISEMENT_SERVICE_UUID
DEFAULT_SERVICE_UUID = '0fda92b2-44a2-4af2-84f5-fa682baa2b8d'
VALID_LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
INVALID_LE_ADVERTISEMENT_IFACE = 'org.fake.iface'


class TestDiagnosticCharacteristic(TestCase):

    # Prevent error log diff from being trimmed
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.service = Service(200, '1111', True)

    def test_instantiation(self):
        diagnostics_characteristic = DiagnosticsCharacteristic(self.service,
                                                               'A1:B2:C3:DD:E5:F6',
                                                               'B1:B2:C3:DD:E5:F6',
                                                               '2021.06.26.4')
        self.assertIsInstance(diagnostics_characteristic, DiagnosticsCharacteristic)

    @patch('dbus.SessionBus')
    @patch('dbus.Interface', return_value=Mock(
        P2PStatus=Mock(return_value={
            'connected': '1',
            'dialable': '0',
            'height': '100',
            'nat_type': 'NAT',
        })))
    def test_get_p2pstatus(self, mock_dbus_session_bus, mock_dbus_interface):
        diagnostics_characteristic = DiagnosticsCharacteristic(self.service,
                                                               'A1:B2:C3:DD:E5:F6',
                                                               'B1:B2:C3:DD:E5:F6',
                                                               '2021.06.26.4')
        p2pstatus = diagnostics_characteristic.get_p2pstatus()
        print("p2pstatus: %s" % p2pstatus)

        expected = {
            'connected': '1',
            'dialable': '0',
            'height': '100',
            'nat_type': 'NAT',
        }
        self.assertDictEqual(p2pstatus, expected)

        mock_dbus_session_bus.assert_called()
        mock_dbus_interface.assert_called()
