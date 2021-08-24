from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.logger import logger
import gatewayconfig.constants as constants

MANUFACTURER_NAME = "Nebra LTD."

class ManufacturerNameCharacteristic(Characteristic):
    def __init__(self, service):
        Characteristic.__init__(
                self, constants.MANUFACTURER_NAME_CHARACTERISTIC_UUID,
                ["read"], service)

    def ReadValue(self, options):
        logger.debug('Read Manufacturer')
        return string_to_dbus_encoded_byte_array(MANUFACTURER_NAME)