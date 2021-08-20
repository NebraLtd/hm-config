import pytest
import sys
import uuid
from io import StringIO
from lib.cputemp.service import Service

from unittest import TestCase
import dbus
import dbus.mainloop.glib
from unittest.mock import patch, mock_open

from gatewayconfig.bluetooth.characteristics.diagnostics_characteristic import DiagnosticsCharacteristic


# Should correspond with BluetoothConnectionAdvertisement.ADVERTISEMENT_SERVICE_UUID
DEFAULT_SERVICE_UUID = '0fda92b2-44a2-4af2-84f5-fa682baa2b8d'
VALID_LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
INVALID_LE_ADVERTISEMENT_IFACE = 'org.fake.iface'

class TestDiagnosticCharacteristic(TestCase):

    # Prevent error log diff from being trimmed
    maxDiff = None

    def test_instantiation(self):
        service = Service(1, '1111', True)
        diagnostics_characteristic = DiagnosticsCharacteristic(service, 'A1:B2:C3:DD:E5:F6', 'B1:B2:C3:DD:E5:F6')
        self.assertEqual(
            diagnostics_characteristic.eth0_mac_address,
            'A1:B2:C3:DD:E5:F6'
        )

        self.assertEqual(
            diagnostics_characteristic.wlan0_mac_address,
            'B1:B2:C3:DD:E5:F6'
        )