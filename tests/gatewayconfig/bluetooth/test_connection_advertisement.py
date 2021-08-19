import pytest
import sys
import uuid
from io import StringIO
from unittest import TestCase
import dbus
import dbus.mainloop.glib
from unittest.mock import patch, mock_open

from gatewayconfig.bluetooth.advertisements.bluetooth_connection_advertisement import BluetoothConnectionAdvertisement


# Should correspond with BluetoothConnectionAdvertisement.ADVERTISEMENT_SERVICE_UUID
DEFAULT_SERVICE_UUID = '0fda92b2-44a2-4af2-84f5-fa682baa2b8d'
VALID_LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
INVALID_LE_ADVERTISEMENT_IFACE = 'org.fake.iface'

class TestBluetoothConnectionAdvertisement(TestCase):

    # Prevent error log diff from being trimmed
    maxDiff = None

    def test_instantiation(self):
        advertisement = BluetoothConnectionAdvertisement(100, 'A1:B2:C3:DD:E5:F6_', 'peripheral_', 'NEBHNT_')
        self.assertEqual(
            advertisement.path,
            '/org/bluez/example/advertisement100'
        )
        self.assertIsInstance(
            advertisement.bus,
            dbus._dbus.SystemBus
        )
        self.assertEqual(
            advertisement.local_name,
            'Nebra DE5F6_ Hotspot (NEBHNT_)'
        )
        self.assertEqual(
            advertisement.ad_type,
            'peripheral_'
        )

    @patch("builtins.open", new_callable=mock_open, read_data='a1:B2:c3:Dd:e5:f6')
    def test_get_properties(self, eth0_file_mock):
        advertisement = BluetoothConnectionAdvertisement(101, 'A1:B2:C3:DD:E5:F6', 'peripheral', 'NEBHNT-IN1')
        properties = advertisement.get_properties()
        expected = {
            'org.bluez.LEAdvertisement1': {
                'Type': 'peripheral',
                'IncludeTxPower': dbus.Boolean(True),
                'LocalName': dbus.String('Nebra %s Hotspot (NEBHNT-IN1)' % 'DDE5F6'),
                'ServiceUUIDs': dbus.Array([DEFAULT_SERVICE_UUID], signature=dbus.Signature('s'))
            }
        }
        self.assertDictEqual(properties, expected)

    def test_get_properties_extended(self):
        advertisement = BluetoothConnectionAdvertisement(102, 'A1:B2:C3:DD:E5:F6', "peripheral", "NEBHNT-IN1")

        service_uuids = [str(uuid.uuid4())]
        advertisement.service_uuids = service_uuids
        advertisement.local_name = 'Local Name'
        solicit_uuids = [str(uuid.uuid4())]
        advertisement.solicit_uuids = solicit_uuids
        manufacturer_data = {'hello': 'manufacturer'}
        advertisement.manufacturer_data = manufacturer_data
        service_data = {'hello': 'service'}
        advertisement.service_data = service_data
        advertisement.include_tx_power = True

        properties = advertisement.get_properties()
        expected = {
            'org.bluez.LEAdvertisement1': {
                'IncludeTxPower': dbus.Boolean(True),
                'LocalName': dbus.String('Local Name'),
                'ManufacturerData': manufacturer_data,
                'ServiceData': service_data,
                'ServiceUUIDs': dbus.Array(
                    service_uuids,
                    signature=dbus.Signature('s')
                ),
                'SolicitUUIDs': dbus.Array(
                    solicit_uuids,
                    signature=dbus.Signature('s')
                ),
                'Type': 'peripheral'
            }
        }
        self.assertDictEqual(properties, expected)

    def test_get_path(self):
        advertisement = BluetoothConnectionAdvertisement(103, 'A1:B2:C3:DD:E5:F6', 'peripheral', 'COMP-HELIUM')
        path = advertisement.get_path()
        self.assertIsInstance(path, dbus.ObjectPath)

    def test_add_service_uuid(self):
        advertisement = BluetoothConnectionAdvertisement(104, 'A1:B2:C3:DD:E5:F6', 'peripheral', 'COMP-HELIUM')
        service_uuid = str(uuid.uuid4())
        advertisement.add_service_uuid(service_uuid)
        # FIXME: There is currently test environment pollution and DEFAULT_SERVICE_ID has been
        # added to the service UUIDs in a previous test. 
        self.assertIn(
            service_uuid,
            advertisement.service_uuids
        )

    def test_add_solicit_uuid(self):
        advertisement = BluetoothConnectionAdvertisement(105, 'A1:B2:C3:DD:E5:F6', 'peripheral', 'COMP-HELIUM')
        solicit_uuid = str(uuid.uuid4())
        advertisement.add_solicit_uuid(solicit_uuid)
        self.assertEqual(
            advertisement.solicit_uuids,
            [solicit_uuid]
        )

    def test_add_manufacturer_data(self):
        advertisement = BluetoothConnectionAdvertisement(106, 'A1:B2:C3:DD:E5:F6', 'peripheral', 'DIY-RAK2287')
        manufacturer_data = {'name': 'Nebra'}
        advertisement.add_manufacturer_data(
            'Nebra',
            manufacturer_data
        )
        self.assertEqual(
            advertisement.manufacturer_data,
            dbus.Dictionary(
                {
                    'Nebra': dbus.Array(
                        ['name'],
                        signature=dbus.Signature('y')
                    )
                },
                signature=dbus.Signature('qv')
            )
        )

    def test_add_service_data(self):
        advertisement = BluetoothConnectionAdvertisement(107, 'A1:B2:C3:DD:E5:F6', 'peripheral', 'DIY-RAK2287')
        service_uuid = str(uuid.uuid4())
        service_data = {'key': 'value'}
        advertisement.add_service_data(
            service_uuid,
            service_data
        )
        self.assertEqual(
            advertisement.service_data,
            dbus.Dictionary(
                {
                    service_uuid: dbus.Array(
                        ['key'],
                        signature=dbus.Signature('y'))
                },
                signature=dbus.Signature('sv')
            )
        )

    def test_add_local_name(self):
        advertisement = BluetoothConnectionAdvertisement(108, 'A1:B2:C3:DD:E5:F6', 'peripheral', 'DIY-RAK2287')
        local_name = 'LocalHost'
        advertisement.add_local_name(
            local_name
        )
        self.assertEqual(
            advertisement.local_name,
            dbus.String(local_name)
        )

    @patch("builtins.open", new_callable=mock_open, read_data='a1:B2:c3:Dd:e5:f6')
    def test_getall_valid_iface(self, eth0_file_mock):
        advertisement = BluetoothConnectionAdvertisement(109, 'A1:B2:C3:DD:E5:F6', 'peripheral', 'NEBHNT-HHTK2')
        self.assertDictEqual(
            advertisement.GetAll(VALID_LE_ADVERTISEMENT_IFACE),
            {
                'IncludeTxPower': dbus.Boolean(True),
                'LocalName': dbus.String('Nebra %s Hotspot (NEBHNT-HHTK2)' % 'DDE5F6'),
                'ServiceUUIDs': dbus.Array([DEFAULT_SERVICE_UUID]),
                'Type': 'peripheral',
            }
        )

    def test_getall_invalid_iface(self):
        advertisement = BluetoothConnectionAdvertisement(110, 'A1:B2:C3:DD:E5:F6', 'peripheral', 'NEBHNT-HHTK2')

        exception = False
        exception_type = None

        try:
            advertisement.GetAll(INVALID_LE_ADVERTISEMENT_IFACE)
        except Exception as err:
            exception = True
            exception_type = err

        self.assertTrue(exception)
        self.assertIsInstance(exception_type, Exception)

    def test_release(self):
        advertisement = BluetoothConnectionAdvertisement(111, 'A1:B2:C3:DD:E5:F6', 'peripheral', 'NEBHNT-HHTK2')

        out = StringIO()
        sys.stdout = out
        result = advertisement.Release()
        printed_output = out.getvalue().strip()
        self.assertEqual(
            printed_output,
            '/org/bluez/example/advertisement111: Released!'
        )

        # Returns nothing
        self.assertEqual(result, None)

    def test_register_callback(self):
        advertisement = BluetoothConnectionAdvertisement(112, 'A1:B2:C3:DD:E5:F6', 'peripheral', 'NEBHNT-HHTK2')

        out = StringIO()
        sys.stdout = out
        result = advertisement.register_ad_callback()
        printed_output = out.getvalue().strip()
        self.assertEqual(
            printed_output,
            'GATT advertisement registered'
        )

        # Returns nothing
        self.assertEqual(result, None)

    def test_register_ad_error_callback(self):
        advertisement = BluetoothConnectionAdvertisement(113, 'A1:B2:C3:DD:E5:F6', 'peripheral', 'NEBHNT-HHTK2')

        out = StringIO()
        sys.stdout = out
        err = 'Error Text'
        result = advertisement.register_ad_error_callback(err)
        printed_output = out.getvalue().strip()
        self.assertEqual(
            printed_output,
            'Failed to register GATT advertisement: Error Text'
        )

        # Returns nothing
        self.assertEqual(result, None)

    @patch('lib.cputemp.bletools.BleTools.get_bus')
    @patch('lib.cputemp.bletools.BleTools.find_adapter')
    @patch('dbus.Interface')
    def test_register(
            self,
            mock_dbus_interface,
            mock_findadapter,
            mock_getbus
    ):
        advertisement = BluetoothConnectionAdvertisement(114, 'A1:B2:C3:DD:E5:F6', 'peripheral', 'NEBHNT-HHTK2')
        result = advertisement.register()

        mock_dbus_interface.assert_called()
        mock_findadapter.assert_called()
        mock_getbus.assert_called_with()

        # Returns nothing
        self.assertEqual(result, None)

    @patch('lib.cputemp.bletools.BleTools.get_bus')
    @patch('lib.cputemp.bletools.BleTools.find_adapter')
    @patch('dbus.Interface')
    def test_unregister(
            self,
            mock_dbus_interface,
            mock_findadapter,
            mock_getbus
    ):
        out = StringIO()
        sys.stdout = out

        advertisement = BluetoothConnectionAdvertisement(115, 'A1:B2:C3:DD:E5:F6', 'peripheral', 'NEBHNT-HHTK2')
        result = advertisement.unregister()

        mock_dbus_interface.assert_called()
        mock_findadapter.assert_called()
        mock_getbus.assert_called_with()

        printed_output = out.getvalue().strip()
        self.assertEqual(
            printed_output,
            'GATT advertisement UNregistered'
        )

        # Returns nothing
        self.assertEqual(result, None)