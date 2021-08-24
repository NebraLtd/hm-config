from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

# Test Cases
import dbus
from lib.cputemp.bletools import BleTools


def return_magic_mock(*args, **kwargs):
    return MagicMock()


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