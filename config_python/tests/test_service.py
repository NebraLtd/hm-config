import sys

from unittest import TestCase
from io import StringIO
from unittest.mock import MagicMock
from unittest.mock import patch

# Test Cases
import dbus
from config_python.service import Application
from config_python.service import Service
from config_python.service import Characteristic
from config_python.service import Descriptor
from config_python.service import InvalidArgsException
from config_python.service import NotSupportedException


TEST_SERVICE_UUID = '7e7aadec-2ec7-47d2-afb3-3c2adca22dee'
TEST_CHARACTERISTIC_UUID = 'db1936d6-f441-434c-a395-a9fc8df65ee3'
TEST_DESCRIPTOR_UUID = '78f2c523-cc2d-45a7-9d39-2ff14f1e3e9b'

VALID_GATT_SERVICE_IFACE = "org.bluez.GattService1"
INVALID_GATT_SERVICE_IFACE = "org.fake.service"

VALID_GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
INVALID_GATT_CHRC_IFACE = "org.fake.characteristic"

VALID_GATT_DESC_IFACE = "org.bluez.GattDescriptor1"
INVALID_GATT_DESC_IFACE = "org.fake.descriptor"


class FixtureTestCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
            self,
            TEST_CHARACTERISTIC_UUID,
            ["read"],
            service
        )


class FixtureTestDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
            self,
            TEST_DESCRIPTOR_UUID,
            ["read"],
            characteristic
        )


class TestApplication(TestCase):
    # Currently DBUS is not mocked for all tests, it isn't used for anything
    # else in the test container so we may as well abuse it.

    # Many of the functions in the code base do some action on dbus but never
    # return anything, in this case we mock dbus and check it has been called
    # accordingly.

    # The app object is shared amongst tests as you may only instantiate one
    # connection to the bus path. Tests are named with a letter to ensure they
    # are ran in the correct (alphabetical) order as the dbus is stateful.
    app = Application()

    class FixtureTestService(Service):
        PATH_BASE = "/org/test/unit/service"

        def __init__(self, index):
            Service.__init__(
                self,
                index,
                TEST_SERVICE_UUID,
                True
            )

    def test_a_instantiation(self):
        print(self.app.__dir__())
        self.assertIsInstance(self.app, Application)
        self.assertIsInstance(self.app.bus, dbus._dbus.SystemBus)
        self.assertEqual(self.app.services, [])  # Initially no services
        self.assertEqual(self.app.path, '/')
        self.assertEqual(self.app.next_index, 0)

    def test_a_get_path(self):
        self.assertEqual(self.app.get_path(), '/')

    def test_a_get_managed_objects(self):
        objects = self.app.GetManagedObjects()
        self.assertEqual(objects, {})  # Initially no objects

    def test_b_add_service(self):
        # Check after registering a service that the service is stored
        # within the application's services list.

        # Create a simple dummy service with known values and try adding it to
        # the application.
        service = self.FixtureTestService(0)
        characteristic = FixtureTestCharacteristic(service)
        descriptor = FixtureTestDescriptor(characteristic)
        characteristic.add_descriptor(descriptor)
        service.add_characteristic(characteristic)
        self.app.add_service(service)
        self.assertIsInstance(self.app.services, list)
        self.assertIsInstance(self.app.services[0], self.FixtureTestService)

    def test_c_get_managed_objects(self):
        # Check after registering a service that the service is returned
        # within the managed objects dictionary.
        objects = self.app.GetManagedObjects()
        expected_objects = {
            dbus.ObjectPath('/org/test/unit/service0'): {
                'org.bluez.GattService1': {
                    'Characteristics': dbus.Array(
                        [
                            dbus.ObjectPath(
                                '/org/test/unit/service0/char0'
                            )
                        ],
                        signature=dbus.Signature('o')
                    ),
                    'Primary': True,
                    'UUID': '7e7aadec-2ec7-47d2-afb3-3c2adca22dee'
                }
            },
            dbus.ObjectPath('/org/test/unit/service0/char0'): {
                'org.bluez.GattCharacteristic1': {
                    'Descriptors': dbus.Array(
                        [
                            dbus.ObjectPath(
                                '/org/test/unit/service0/char0/desc0'
                            )
                        ],
                        signature=dbus.Signature('o')
                    ),
                    'Flags': ['read'],
                    'Service': dbus.ObjectPath('/org/test/unit/service0'),
                    'UUID': 'db1936d6-f441-434c-a395-a9fc8df65ee3'
                }
            },
            dbus.ObjectPath('/org/test/unit/service0/char0/desc0'): {
                'org.bluez.GattDescriptor1': {
                    'Characteristic':
                        dbus.ObjectPath('/org/test/unit/service0/char0'),
                    'Flags': ['read'],
                    'UUID': '78f2c523-cc2d-45a7-9d39-2ff14f1e3e9b'
                }
            }
        }
        self.assertEqual(objects, expected_objects)

    def test_d_register_app_callback(self):
        # This method seems to just print some stuff to stdout,
        # probably not mega important but lets check it keeps doing
        # it.
        out = StringIO()
        sys.stdout = out
        self.app.register_app_callback()
        printed_output = out.getvalue().strip()
        self.assertEqual(printed_output, 'GATT application registered')

    def test_d_register_app_error_callback(self):
        # This method seems to just print some stuff to stdout,
        # probably not mega important but lets check it keeps doing
        # it.
        out = StringIO()
        sys.stdout = out
        msg = 'Error Here'
        self.app.register_app_error_callback(msg)
        printed_output = out.getvalue().strip()
        self.assertEqual(
            printed_output,
            'Failed to register application: Error Here'
        )

    @patch('bletools.BleTools.find_adapter')
    @patch('dbus.Interface')
    def test_e_register(self, mock_dbus_interface, mock_find_adapter):
        self.app.bus = MagicMock()
        self.app.register()

        # Check the expected methods are called
        mock_find_adapter.assert_called()
        mock_dbus_interface.assert_called()
        self.app.bus.get_object.assert_called()

        # Check the expected methods are called with the expected args
        mock_find_adapter.assert_called_once_with(self.app.bus)
        mock_dbus_interface.assert_called_once_with(
            self.app.bus.get_object(),
            'org.bluez.GattManager1'
        )

    def test_f_run(self):
        self.app.mainloop = MagicMock()
        self.app.run()

        # Check the mainloop is actually run.
        self.app.mainloop.run.assert_called()

    def test_g_quit(self):
        self.app.mainloop = MagicMock()

        out = StringIO()
        sys.stdout = out
        self.app.quit()
        printed_output = out.getvalue().strip()

        # Check the debug text is printed on quit.
        self.assertEqual(
            printed_output,
            'GATT application terminated'
        )

        # Check the mainloop is actually quit.
        self.app.mainloop.quit.assert_called()


class TestService(TestCase):
    service = Service(
        0,
        TEST_SERVICE_UUID,
        True
    )

    expected_path = '/org/bluez/example/service0'

    def test_a_instantiation(self):
        # Check we can instantiate a service and check it's
        # initial attrs are as expected
        self.assertIsInstance(self.service.bus, dbus._dbus.SystemBus)
        self.assertEqual(self.service.path, self.expected_path)
        self.assertEqual(self.service.uuid, TEST_SERVICE_UUID)
        self.assertTrue(self.service.primary)
        self.assertEqual(self.service.characteristics, [])
        self.assertEqual(self.service.next_index, 0)

    def test_b_get_properties(self):
        properties = self.service.get_properties()
        expected = {
            'org.bluez.GattService1': {
                'Characteristics': dbus.Array(
                    [],
                    signature=dbus.Signature('o')
                ),
                'Primary': True,
                'UUID': TEST_SERVICE_UUID
            }
        }
        self.assertEqual(properties, expected)

    def test_c_get_path(self):
        # Expect a dbus ObjectPath to be returned
        path = self.service.get_path()
        self.assertEqual(path, dbus.ObjectPath(self.expected_path))

    def test_d_add_characteristic(self):
        # Test that we can add a characteristic to the service and
        # that it is returned when we fetch the service's properties
        characteristic = FixtureTestCharacteristic(self.service)
        self.service.add_characteristic(characteristic)
        properties = self.service.get_properties()

        expected = {
            'org.bluez.GattService1': {
                'Characteristics': dbus.Array(
                    [
                        dbus.ObjectPath('/org/bluez/example/service0/char0')
                    ], signature=dbus.Signature('o')
                ),
                'Primary': True,
                'UUID': TEST_SERVICE_UUID
            }
        }

        self.assertEqual(properties, expected)

    def test_e_get_characteristic_paths(self):
        # Expect a list of ObjectPaths to be  returned
        paths = self.service.get_characteristic_paths()
        expected = [dbus.ObjectPath('/org/bluez/example/service0/char0')]
        self.assertEqual(paths, expected)

    def test_f_get_bus(self):
        # Expect a dbus SystemBus object to be returned
        bus = self.service.get_bus()
        self.assertIsInstance(bus, dbus._dbus.SystemBus)

    def test_g_get_next_index(self):
        # Check that an integer is returned and that the next
        # index is incremented by 1.
        current_value = self.service.next_index
        return_value = self.service.get_next_index()
        new_value = self.service.next_index

        self.assertIsInstance(current_value, int)
        self.assertIsInstance(return_value, int)
        self.assertEqual(new_value, current_value + 1)

    def test_h_get_all_valid_interface(self):
        # Check that relevant properties are returned when a valid
        # interface is provided.
        properties = self.service.GetAll(VALID_GATT_SERVICE_IFACE)
        expected = {
            'Characteristics': dbus.Array(
                [
                    dbus.ObjectPath('/org/bluez/example/service0/char0')
                ],
                signature=dbus.Signature('o')
            ),
            'Primary': True,
            'UUID': TEST_SERVICE_UUID
        }
        self.assertEqual(properties, expected)

    def test_h_get_all_invalid_interface(self):
        # Check that InvalidArgsException is thrown when an invalid
        # interface is provided to the GetAll method.
        exception = False
        exception_type = None
        try:
            self.service.GetAll(INVALID_GATT_SERVICE_IFACE)
        except Exception as err:
            exception = True
            exception_type = err

        self.assertTrue(exception)
        self.assertIsInstance(exception_type, InvalidArgsException)


class TestCharacteristic(TestCase):

    class FixtureTestService(Service):
        PATH_BASE = "/org/test/unit/service1"

        def __init__(self, index):
            Service.__init__(
                self,
                index,
                TEST_SERVICE_UUID,
                True
            )

    service = FixtureTestService(0)

    characteristic = Characteristic(
        TEST_CHARACTERISTIC_UUID,
        ["read"],
        service
    )

    def test_a_instantiation(self):
        # Check that the instantiated characteristic has the expected
        # attributes
        self.assertEqual(
            self.characteristic.path,
            '/org/test/unit/service10/char0'
        )
        self.assertIsInstance(
            self.characteristic.bus,
            dbus._dbus.SystemBus
        )
        self.assertEqual(
            self.characteristic.uuid,
            TEST_CHARACTERISTIC_UUID
        )
        self.assertIsInstance(
            self.characteristic.service,
            self.FixtureTestService
        )
        self.assertEqual(
            self.characteristic.flags,
            ['read']
        )
        self.assertEqual(self.characteristic.descriptors, [])
        self.assertEqual(self.characteristic.next_index, 0)

    def test_b_get_properties(self):
        # Check the expected properties are returned
        properties = self.characteristic.get_properties()
        expected = {
            'org.bluez.GattCharacteristic1': {
                'Descriptors': dbus.Array(
                    [],
                    signature=dbus.Signature('o')
                ),
                'Flags': ['read'],
                'Service': dbus.ObjectPath('/org/test/unit/service10'),
                'UUID': TEST_CHARACTERISTIC_UUID}}
        self.assertEqual(properties, expected)

    def test_c_get_path(self):
        path = self.characteristic.get_path()
        self.assertEqual(
            path,
            dbus.ObjectPath('/org/test/unit/service10/char0')
        )

    def test_d_add_descriptor(self):
        # Add a descriptor to the characteristic and check the properties
        # are extended accordingly.
        descriptor = FixtureTestDescriptor(self.characteristic)
        self.characteristic.add_descriptor(descriptor)
        expected = {
            'org.bluez.GattCharacteristic1': {
                'Descriptors': dbus.Array(
                    [
                        dbus.ObjectPath('/org/test/unit/service10/char0/desc0')
                    ],
                    signature=dbus.Signature('o')
                ),
                'Flags': ['read'],
                'Service': dbus.ObjectPath('/org/test/unit/service10'),
                'UUID': TEST_CHARACTERISTIC_UUID
            }
        }
        properties = self.characteristic.get_properties()
        self.assertEqual(properties, expected)

    def test_e_get_descriptor_paths(self):
        # Fetch the path of the added descriptor.
        paths = self.characteristic.get_descriptor_paths()
        expected = [
            dbus.ObjectPath('/org/test/unit/service10/char0/desc0')
        ]
        self.assertEqual(paths, expected)

    def test_f_get_descriptors(self):
        # Expect a list of descriptors to be returned
        descriptors = self.characteristic.get_descriptors()
        self.assertIsInstance(descriptors, list)
        for descriptor in descriptors:
            self.assertIsInstance(descriptor, FixtureTestDescriptor)

    def test_g_get_all_valid_interface(self):
        # Check properties are returned with a valid interface.
        properties = self.characteristic.GetAll(VALID_GATT_CHRC_IFACE)
        expected = {
            'Descriptors': dbus.Array(
                [
                    dbus.ObjectPath('/org/test/unit/service10/char0/desc0')
                ],
                signature=dbus.Signature('o')
            ),
            'Flags': ['read'],
            'Service': dbus.ObjectPath('/org/test/unit/service10'),
            'UUID': TEST_CHARACTERISTIC_UUID}
        self.assertEqual(properties, expected)

    def test_g_get_all_invalid_interface(self):
        # Check that InvalidArgsException is thrown when an invalid
        # interface is provided to the GetAll method.
        exception = False
        exception_type = None
        try:
            self.characteristic.GetAll(INVALID_GATT_CHRC_IFACE)
        except Exception as err:
            exception = True
            exception_type = err

        self.assertTrue(exception)
        self.assertIsInstance(exception_type, InvalidArgsException)

    def test_h_read_value(self):
        # This method isn't implemented so should raise a
        # NotSupportedException
        exception = False
        exception_type = None
        try:
            self.characteristic.ReadValue(None)
        except Exception as err:
            exception = True
            exception_type = err

        self.assertTrue(exception)
        self.assertIsInstance(exception_type, NotSupportedException)

    def test_h_write_value(self):
        # This method isn't implemented so should raise a
        # NotSupportedException
        exception = False
        exception_type = None
        try:
            self.characteristic.WriteValue(None, None)
        except Exception as err:
            exception = True
            exception_type = err

        self.assertTrue(exception)
        self.assertIsInstance(exception_type, NotSupportedException)

    def test_h_start_notify(self):
        # This method isn't implemented so should raise a
        # NotSupportedException
        exception = False
        exception_type = None
        try:
            self.characteristic.StartNotify()
        except Exception as err:
            exception = True
            exception_type = err

        self.assertTrue(exception)
        self.assertIsInstance(exception_type, NotSupportedException)

    def test_h_stop_notify(self):
        # This method isn't implemented so should raise a
        # NotSupportedException
        exception = False
        exception_type = None
        try:
            self.characteristic.StopNotify()
        except Exception as err:
            exception = True
            exception_type = err

        self.assertTrue(exception)
        self.assertIsInstance(exception_type, NotSupportedException)

    def test_i_get_bus(self):
        bus = self.characteristic.get_bus()
        self.assertIsInstance(bus, dbus._dbus.SystemBus)

    def test_i_get_next_index(self):
        # Check that an integer is returned and that the next
        # index is incremented by 1.
        current_value = self.characteristic.next_index
        return_value = self.characteristic.get_next_index()
        new_value = self.characteristic.next_index

        self.assertIsInstance(current_value, int)
        self.assertIsInstance(return_value, int)
        self.assertEqual(new_value, current_value + 1)

    @patch('gi.repository.GObject.timeout_add')
    def test_j_add_timeout(self, mock_timeout):
        # Ensure GObject timeout is set when add timeout is called...
        self.characteristic.add_timeout(60, None)
        mock_timeout.assert_called()


class TestDescriptor(TestCase):

    class FixtureTestService(Service):
        PATH_BASE = "/org/test/unit/service2"

        def __init__(self, index):
            Service.__init__(
                self,
                index,
                TEST_SERVICE_UUID,
                True
            )

    service = FixtureTestService(0)

    characteristic = Characteristic(
        TEST_CHARACTERISTIC_UUID,
        ["read"],
        service
    )

    descriptor = Descriptor(
        TEST_DESCRIPTOR_UUID,
        ["read"],
        characteristic
    )

    characteristic.add_descriptor(descriptor)

    def test_a_instantiation(self):
        # Check the descriptor is instantiated with the expected attributes
        self.assertEqual(
            self.descriptor.path,
            '/org/test/unit/service20/char0/desc0'
        )
        self.assertEqual(
            self.descriptor.uuid,
            TEST_DESCRIPTOR_UUID
        )
        self.assertEqual(
            self.descriptor.flags,
            ["read"]
        )
        self.assertEqual(
            self.descriptor.chrc,
            self.characteristic
        )
        self.assertIsInstance(
            self.descriptor.bus,
            dbus._dbus.SystemBus
        )

    def test_b_get_properties(self):
        properties = self.descriptor.get_properties()
        expected = {
            'org.bluez.GattDescriptor1': {
                'Characteristic':
                    dbus.ObjectPath('/org/test/unit/service20/char0'),
                'Flags': ['read'],
                'UUID': TEST_DESCRIPTOR_UUID
            }
        }
        self.assertEqual(properties, expected)

    def test_c_get_all_valid_interface(self):
        properties = self.descriptor.GetAll(VALID_GATT_DESC_IFACE)
        expected = {
            'Characteristic':
                dbus.ObjectPath('/org/test/unit/service20/char0'),
            'Flags': ['read'],
            'UUID': TEST_DESCRIPTOR_UUID
        }
        self.assertEqual(properties, expected)

    def test_c_get_all_invalid_interface(self):
        exception = False
        exception_type = None

        try:
            self.descriptor.GetAll(INVALID_GATT_DESC_IFACE)
        except Exception as err:
            exception = True
            exception_type = err

        self.assertTrue(exception)
        self.assertIsInstance(exception_type, InvalidArgsException)

    def test_d_read_value(self):
        exception = False
        exception_type = None

        try:
            self.descriptor.ReadValue(None)
        except Exception as err:
            exception = True
            exception_type = err

        self.assertTrue(exception)
        self.assertIsInstance(exception_type, NotSupportedException)

    def test_d_write_value(self):
        exception = False
        exception_type = None

        try:
            self.descriptor.WriteValue(None, None)
        except Exception as err:
            exception = True
            exception_type = err

        self.assertTrue(exception)
        self.assertIsInstance(exception_type, NotSupportedException)
