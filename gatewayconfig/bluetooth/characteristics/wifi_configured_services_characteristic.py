
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
        # logger.debug("Constructed WifiConfiguredServicesCharacteristic %s" % self.shared_state.to_s())

    def ReadValue(self, options):
        logger.debug("Read Wifi CONFIGURED Services")
        try:
            configured_wifi_services = wifi_services_pb2.wifi_services_v1()

            # logger.debug("Read configured_wifi_services %s" % self.shared_state.to_s())
            wifi_list_cache = self.shared_state.wifi_list_cache

            logger.debug("Looping through wifi cache of %s objects" % len(wifi_list_cache))
            for network in wifi_list_cache:
                ssid_str = str(network.ssid)
                logger.debug("Considering network %s" % ssid_str)

                if(is_valid_ssid(ssid_str)):
                    logger.debug("%s is a valid SSID" % ssid_str)
                    if(network.in_use):
                        logger.debug("Adding network %s to configured wifi services")
                        configured_wifi_services.services.append(ssid_str)

            return string_to_dbus_byte_array(configured_wifi_services.SerializeToString())

        except Exception:
            logger.exception("Wifi configured characteristic failed for unknown reason")
