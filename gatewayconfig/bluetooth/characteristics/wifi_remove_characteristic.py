
from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.logger import get_logger
from gatewayconfig.bluetooth.descriptors.wifi_remove_descriptor import WifiRemoveDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.nmcli_custom as nmcli_custom
import gatewayconfig.protos.wifi_remove_pb2 as wifi_remove_pb2
import gatewayconfig.constants as constants

logger = get_logger(__name__)


class WifiRemoveCharacteristic(Characteristic):

    def __init__(self, service):
        self.notifying = False
        Characteristic.__init__(
                self, constants.WIFI_REMOVE_CHARACTERISTIC_UUID,
                ["read", "write", "notify"], service)
        self.add_descriptor(WifiRemoveDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))
        self.wifi_status = "False"

    def wifi_remove_callback(self):
        if self.notifying:
            logger.debug('Callback WiFi Remove')
            value = string_to_dbus_encoded_byte_array(self.wifi_status)
            self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):

        logger.debug('Notify WiFi Remove')
        if self.notifying:
            return

        self.notifying = True

        value = string_to_dbus_encoded_byte_array(self.wifi_status)
        self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(30000, self.wifi_remove_callback)

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logger.debug('Write WiFi Remove')
        wifi_remove_ssid = wifi_remove_pb2.wifi_remove_v1()
        wifi_remove_ssid.ParseFromString(bytes(value))
        nmcli_custom.connection.delete(wifi_remove_ssid.service)
        logger.debug('Connection %s should be deleted'
                     % wifi_remove_ssid.service)

    def ReadValue(self, options):
        logger.debug('Read WiFi Remove')
        return string_to_dbus_encoded_byte_array(self.WIFI_STATUSES)
