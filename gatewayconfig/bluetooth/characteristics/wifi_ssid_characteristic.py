
from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import is_valid_ssid, string_to_dbus_encoded_byte_array
from gatewayconfig.logger import get_logger
from gatewayconfig.bluetooth.descriptors.wifi_ssid_descriptor import WifiSSIDDescriptor
from gatewayconfig.bluetooth.descriptors.utf8_format_descriptor import UTF8FormatDescriptor
import gatewayconfig.constants as constants

logger = get_logger(__name__)


class WifiSSIDCharacteristic(Characteristic):

    def __init__(self, service, shared_state):
        Characteristic.__init__(
                self, constants.WIFI_SSID_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(WifiSSIDDescriptor(self))
        self.add_descriptor(UTF8FormatDescriptor(self))
        self.shared_state = shared_state

    def ReadValue(self, options):

        logger.debug('Read WiFi SSID')
        active_connection = ""
        for network in self.shared_state.wifi_list_cache:
            ssid_str = str(network.ssid)

            if(is_valid_ssid(ssid_str)):
                if(network.in_use):
                    logger.debug("SSID in use: %s" % ssid_str)
                    active_connection = ssid_str
                else:
                    logger.debug("SSID not in use: %s" % ssid_str)
            else:
                logger.debug("Ignoring SSID: %s" % ssid_str)

        return string_to_dbus_encoded_byte_array(active_connection)
