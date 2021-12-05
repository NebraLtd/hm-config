import dbus

from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import is_valid_ssid
from gatewayconfig.logger import get_logger
from gatewayconfig.bluetooth.descriptors.wifi_services_descriptor import WifiServicesDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.constants as constants
import gatewayconfig.protos.wifi_services_pb2 as wifi_services_pb2

logger = get_logger(__name__)


class WifiServicesCharacteristic(Characteristic):

    def __init__(self, service, shared_state):
        Characteristic.__init__(
                self, constants.WIFI_SERVICES_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(WifiServicesDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))
        self.shared_state = shared_state

    def ReadValue(self, options):
        logger.debug('Read WiFi Services')
        try:
            known_wifi_services = wifi_services_pb2.wifi_services_v1()

            # logger.debug("Cached WIFI %s" % self.shared_state.wifi_list_cache)
            for network in self.shared_state.wifi_list_cache:
                ssid_str = str(network.ssid)
                logger.debug("Inspecting SSID %s" % ssid_str)

                if(is_valid_ssid(ssid_str)):
                    logger.debug("%s is a valid ssid" % ssid_str)
                    ssid_unknown = ssid_str not in known_wifi_services.services

                    if(ssid_unknown):
                        logger.debug("%s ssid is unknown" % ssid_str)
                        known_wifi_services.services.append(ssid_str)

            logger.debug("Finished getting known wifi services")
            value = []
            val = known_wifi_services.SerializeToString()
            logger.debug("Going to write %s" % val)
            for c in val:
                value.append(dbus.Byte(c))
            if("offset" in options):
                cutDownArray = value[int(options["offset"]):]
                return cutDownArray
            else:
                return value

        except Exception:
            logger.exception('WifiServicesCharacteristic failed for unknown reason')
