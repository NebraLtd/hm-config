from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import string_to_dbus_byte_array
from gatewayconfig.logger import logger
from gatewayconfig.bluetooth.descriptors.ethernet_online_descriptor import EthernetOnlineDescriptor
from gatewayconfig.bluetooth.descriptors.utf8_format_descriptor import UTF8FormatDescriptor

import gatewayconfig.constants as constants


ETHERNET_IS_ONLINE_CARRIER_VAL = "1"

class EthernetOnlineCharacteristic(Characteristic):

    def __init__(self, service, ethernet_is_online_filepath):
        Characteristic.__init__(
                self, constants.ETHERNET_ONLINE_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(EthernetOnlineDescriptor(self))
        self.add_descriptor(UTF8FormatDescriptor(self))
        self.ethernet_is_online_filepath = ethernet_is_online_filepath

    def ReadValue(self, options):
        logger.debug('Read Ethernet Online')

        is_ethernet_online = "false"

        ethernet_is_online_carrier_val = open(self.ethernet_is_online_filepath).readline().strip()
        if(ethernet_is_online_carrier_val == ETHERNET_IS_ONLINE_CARRIER_VAL):
            is_ethernet_online = "true"

        logger.debug("Ethernet is online: %s" % is_ethernet_online)
        return string_to_dbus_byte_array(is_ethernet_online)