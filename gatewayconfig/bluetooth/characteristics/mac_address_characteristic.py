from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.logger import get_logger
from gatewayconfig.bluetooth.descriptors.mac_address_descriptor import MacAddressDescriptor
from gatewayconfig.bluetooth.descriptors.utf8_format_descriptor import UTF8FormatDescriptor
import gatewayconfig.constants as constants

logger = get_logger(__name__)


class MacAddressCharacteristic(Characteristic):

    def __init__(self, service, eth0_mac_address):
        Characteristic.__init__(
                self, constants.MAC_ADDRESS_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(MacAddressDescriptor(self))
        self.add_descriptor(UTF8FormatDescriptor(self))
        self.eth0_mac_address = eth0_mac_address.replace(':', '')

    def ReadValue(self, options):
        logger.debug('Read Mac Address')
        return string_to_dbus_encoded_byte_array(self.eth0_mac_address)
