from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import dbus
from gatewayconfig.processors.bluetooth_services_processor import \
    BluetoothServicesProcessor
from lib.cputemp.advertisement import Advertisement
from lib.cputemp.bletools import BleTools


def return_magic_mock(*args, **kwargs):
    return MagicMock()


def system_bus_no_ble_side_effect(*args, **kwargs):
    def get_object_side_effect(bus_name, object_path):
        # When there is no BLE adapter, object_path became None
        # it should raise an exception
        if not object_path:
            raise TypeError()
        return MagicMock()

    mock_dbus = MagicMock()
    mock_dbus.get_object = MagicMock()
    mock_dbus.get_object.side_effect = get_object_side_effect
    return mock_dbus


class TestBleTools(TestCase):

    def test_get_bus(self):
        # Should return an instance of dbus SystemBus
        bus = BleTools.get_bus()
        self.assertIsInstance(bus, dbus._dbus.SystemBus)

    @patch('dbus.Interface', side_effect=return_magic_mock)
    def test_find_adapter(self, mock_dbus_interface):
        bus = MagicMock()
        result = BleTools.find_adapter(bus)
        mock_dbus_interface.assert_called()
        bus.get_object.assert_called()
        self.assertEqual(result, None)

    # Test BluetoothServicesProcessor
    @patch('dbus.SystemBus')
    @patch('dbus.Interface')
    def test_service_no_adapter(self, mocked_interface, mocked_system_bus):
        mocked_system_bus.side_effect = system_bus_no_ble_side_effect

        eth0_mac_address = ""
        wlan0_mac_address = ""
        firmware_version = ""
        ethernet_is_online_filepath = ""
        shared_state = {}

        try:
            with self.assertLogs('lib.cputemp', level='DEBUG') as cm:
                BluetoothServicesProcessor(
                    eth0_mac_address,
                    wlan0_mac_address,
                    firmware_version,
                    ethernet_is_online_filepath,
                    shared_state)
                self.assertIn('ERROR:lib.cputemp.service:'
                              'Unable to start Bluetooth application: '
                              'No Bluetooth Adapter',
                              cm.output)
        except TypeError:
            self.fail("Exception raised when no BT adapter")

    # Test Advertisement
    @patch('dbus.SystemBus')
    @patch('dbus.Interface')
    def test_advertise_no_adapter(self, mocked_interface, mocked_system_bus):
        mocked_system_bus.side_effect = system_bus_no_ble_side_effect

        index = 0
        advertising_type = "peripheral"
        try:
            with self.assertLogs('lib.cputemp',
                                 level='DEBUG') as cm:
                ble_advertisement = Advertisement(index, advertising_type)
                ble_advertisement.register()
                self.assertIn('ERROR:lib.cputemp.advertisement:'
                              'Unable to start Advertisement: '
                              'No Bluetooth adapter.',
                              cm.output)
        except TypeError:
            self.fail("Exception raised when no BT adapter")

    @patch('dbus.Interface', side_effect=return_magic_mock)
    def test_find_connection(self, mock_dbus_interface):
        bus = MagicMock()
        result = BleTools.find_connection(bus)
        mock_dbus_interface.assert_called()
        bus.get_object.assert_called()
        self.assertEqual(result, None)

    @patch('dbus.Interface', side_effect=return_magic_mock)
    @patch(
        'lib.cputemp.bletools.BleTools.get_bus',
        side_effect=return_magic_mock
    )
    def test_disconnect_connections(
            self,
            mock_get_bus,
            mock_dbus_interface
    ):
        result = BleTools.disconnect_connections()
        mock_dbus_interface.assert_called()
        mock_get_bus.assert_called()
        self.assertEqual(result, None)
