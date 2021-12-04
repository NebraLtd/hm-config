from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.logger import get_logger
from gatewayconfig.file_loader import read_ethernet_is_online
from gatewayconfig.bluetooth.descriptors.ethernet_online_descriptor import EthernetOnlineDescriptor
from gatewayconfig.bluetooth.descriptors.utf8_format_descriptor import UTF8FormatDescriptor

import gatewayconfig.constants as constants

logger = get_logger(__name__)


class EthernetOnlineCharacteristic(Characteristic):

    def __init__(self, service, ethernet_is_online_filepath):
        Characteristic.__init__(
                self, constants.ETHERNET_ONLINE_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(EthernetOnlineDescriptor(self))
        self.add_descriptor(UTF8FormatDescriptor(self))
        self.ethernet_is_online_filepath = ethernet_is_online_filepath

    def ReadValue(self, options):
        logger.debug("Read Ethernet Online from %s" % self.ethernet_is_online_filepath)

        is_ethernet_online = read_ethernet_is_online(self.ethernet_is_online_filepath)
        logger.debug("Ethernet is online: %s" % is_ethernet_online)
        return string_to_dbus_encoded_byte_array(is_ethernet_online)
