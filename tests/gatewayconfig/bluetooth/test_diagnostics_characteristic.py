from lib.cputemp.service import Service
from unittest import TestCase
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
