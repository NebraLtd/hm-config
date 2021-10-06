from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.logger import get_logger
import gatewayconfig.constants as constants

logger = get_logger(__name__)


class SerialNumberCharacteristic(Characteristic):

    def __init__(self, service, eth0_mac_address):
        Characteristic.__init__(
                self, constants.SERIAL_NUMBER_CHARACTERISTIC_UUID,
                ["read"], service)

        self.formatted_eth_mac_address = eth0_mac_address.replace(":", "")

    def ReadValue(self, options):
        logger.debug('Read Serial Number')
        return string_to_dbus_encoded_byte_array(self.formatted_eth_mac_address)
