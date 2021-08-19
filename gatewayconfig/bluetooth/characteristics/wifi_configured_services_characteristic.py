
from lib.cputemp.service import Characteristic
import gatewayconfig.protos as protos

from gatewayconfig.helpers import is_valid_ssid, string_to_dbus_byte_array
from gatewayconfig.logger import logger
from gatewayconfig.bluetooth.descriptors.wifi_configured_services_descriptor import WifiConfiguredServicesDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.protos as protos
import gatewayconfig.constants as constants


class WifiConfiguredServicesCharacteristic(Characteristic):

    def __init__(self, service, shared_state):
        Characteristic.__init__(
                self, constants.WIFI_CONFIGURED_SERVICES_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(WifiConfiguredServicesDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))
        self.shared_state = shared_state

    def ReadValue(self, options):
        logger.debug('Read WiFi CONFIGURED Services')
        configured_wifi_services = protos.wifi_services_pb2.wifi_services_v1()


        for network in self.shared_state.wifi_list_cache:
            ssid_str = str(network.ssid)

            if(is_valid_ssid(ssid_str)):
                if(network.in_use):
                    configured_wifi_services.services.append(ssid_str)

        return string_to_dbus_byte_array(configured_wifi_services.SerializeToString())
