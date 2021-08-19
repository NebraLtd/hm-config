import logging
import dbus

from lib.cputemp.service import Characteristic
from gatewayconfig.bluetooth.descriptors.ethernet_online_descriptor import EthernetOnlineDescriptor
from gatewayconfig.bluetooth.descriptors.utf8_format_descriptor import UTF8FormatDescriptor
import gatewayconfig.constants as constants

class EthernetOnlineCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, constants.ETHERNET_ONLINE_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(EthernetOnlineDescriptor(self))
        self.add_descriptor(UTF8FormatDescriptor(self))

    def ReadValue(self, options):

        logging.debug('Read Ethernet Online')

        value = []

        val = "false"

        if(open("/sys/class/net/eth0/carrier").readline().strip() == "1"):
            val = "true"

        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value