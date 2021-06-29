import uuid
import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

# Test Cases
import dbus
from config_python.advertisement import Advertisement


VALID_LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"
INVALID_LE_ADVERTISEMENT_IFACE = "org.fake.iface"


class TestAdvertisement(TestCase):

    def test_instantiation(self):
        advertisement = Advertisement(5, "peripheral")

        self.assertEqual(
            advertisement.path,
            '/org/bluez/example/advertisement5'
        )
        self.assertIsInstance(
            advertisement.bus,
            dbus._dbus.SystemBus
        )
        self.assertEqual(
            advertisement.ad_type,
            'peripheral'
        )

    def test_get_properties(self):
        advertisement = Advertisement(10, "peripheral")
        properties = advertisement.get_properties()
        expected = {
            'org.bluez.LEAdvertisement1': {
                'Type': 'peripheral'
            }
        }
        self.assertEqual(properties, expected)

    def test_get_properties_extended(self):
        advertisement = Advertisement(15, "peripheral")

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
        self.assertEqual(properties, expected)

    def test_get_path(self):
        advertisement = Advertisement(20, "peripheral")
        path = advertisement.get_path()
        self.assertIsInstance(path, dbus.ObjectPath)

    def test_add_service_uuid(self):
        advertisement = Advertisement(25, "peripheral")
        service_uuid = str(uuid.uuid4())
        advertisement.add_service_uuid(service_uuid)
        self.assertEqual(
            advertisement.service_uuids,
            [service_uuid]
        )

    def test_add_solicit_uuid(self):
        advertisement = Advertisement(30, "peripheral")
        solicit_uuid = str(uuid.uuid4())
        advertisement.add_solicit_uuid(solicit_uuid)
        self.assertEqual(
            advertisement.solicit_uuids,
            [solicit_uuid]
        )

    def test_add_manufacturer_data(self):
        advertisement = Advertisement(35, "peripheral")
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
        advertisement = Advertisement(40, "peripheral")
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
        advertisement = Advertisement(45, "peripheral")
        local_name = 'LocalHost'
        advertisement.add_local_name(
            local_name
        )
        self.assertEqual(
            advertisement.local_name,
            dbus.String(local_name)
        )

    def test_getall_valid_iface(self):
        advertisement = Advertisement(50, "peripheral")
        self.assertEqual(
            advertisement.GetAll(VALID_LE_ADVERTISEMENT_IFACE),
            {'Type': 'peripheral'}
        )

    def test_getall_invalid_iface(self):
        advertisement = Advertisement(55, "peripheral")

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
        advertisement = Advertisement(60, "peripheral")

        out = StringIO()
        sys.stdout = out
        result = advertisement.Release()
        printed_output = out.getvalue().strip()
        self.assertEqual(
            printed_output,
            '/org/bluez/example/advertisement60: Released!'
        )

        # Returns nothing
        self.assertEqual(result, None)

    def test_register_callback(self):
        advertisement = Advertisement(65, "peripheral")

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
        advertisement = Advertisement(70, "peripheral")

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

    @patch('bletools.BleTools.get_bus')
    @patch('bletools.BleTools.find_adapter')
    @patch('dbus.Interface')
    def test_register(
            self,
            mock_dbus_interface,
            mock_findadapter,
            mock_getbus
    ):
        advertisement = Advertisement(75, "peripheral")
        result = advertisement.register()

        mock_dbus_interface.assert_called()
        mock_findadapter.assert_called()
        mock_getbus.assert_called_with()

        # Returns nothing
        self.assertEqual(result, None)

    @patch('bletools.BleTools.get_bus')
    @patch('bletools.BleTools.find_adapter')
    @patch('dbus.Interface')
    def test_unregister(
            self,
            mock_dbus_interface,
            mock_findadapter,
            mock_getbus
    ):
        out = StringIO()
        sys.stdout = out

        advertisement = Advertisement(80, "peripheral")
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
