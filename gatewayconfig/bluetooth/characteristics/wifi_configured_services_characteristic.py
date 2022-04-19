from lib import nmcli_custom
from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import is_valid_ssid, string_to_dbus_byte_array
from gatewayconfig.logger import get_logger
from gatewayconfig.bluetooth.descriptors.wifi_configured_services_descriptor import WifiConfiguredServicesDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.protos.wifi_services_pb2 as wifi_services_pb2
import gatewayconfig.constants as constants

logger = get_logger(__name__)


class WifiConfiguredServicesCharacteristic(Characteristic):

    def __init__(self, service, shared_state):
        Characteristic.__init__(
                self, constants.WIFI_CONFIGURED_SERVICES_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(WifiConfiguredServicesDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))
        self.shared_state = shared_state

    def ReadValue(self, options):
        logger.debug("Read Wifi CONFIGURED Services")
        try:
            configured_wifi_services = wifi_services_pb2.wifi_services_v1()

            connections = nmcli_custom.connection()
            for connection in connections:
                logger.debug("Considering connection %s" % connection.name)

                if connection.conn_type == 'wifi':
                    logger.debug("Adding connection %s to configured wifi services")
                    configured_wifi_services.services.append(connection.name)

            return string_to_dbus_byte_array(configured_wifi_services.SerializeToString())

        except Exception as e:
            logger.exception("Wifi configured characteristic failed for unknown reason: %s" % str(e))
