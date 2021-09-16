
from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.logger import get_logger
import gatewayconfig.constants as constants

logger = get_logger(__name__)


class SoftwareVersionCharacteristic(Characteristic):
    def __init__(self, service, firmware_version):
        Characteristic.__init__(
                self, constants.SOFTWARE_VERSION_CHARACTERISTIC_UUID,
                ["read"], service)
        self.firmware_version = firmware_version

    def ReadValue(self, options):
        logger.debug('Read Firmware')
        return string_to_dbus_encoded_byte_array(self.firmware_version)
