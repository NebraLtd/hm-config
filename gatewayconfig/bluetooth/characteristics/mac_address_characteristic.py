import logging
import dbus

from lib.cputemp.service import Characteristic

from gatewayconfig.bluetooth.descriptors.mac_address_descriptor import MacAddressDescriptor
from gatewayconfig.bluetooth.descriptors.utf8_format_descriptor import UTF8FormatDescriptor
import gatewayconfig.constants as constants

class MacAddressCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, constants.MAC_ADDRESS_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(MacAddressDescriptor(self))
        self.add_descriptor(UTF8FormatDescriptor(self))

    def ReadValue(self, options):
        logging.debug('Read Mac Address')
        value = []
        val = open("/sys/class/net/eth0/address").readline().strip() \
            .replace(":", "")

        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value