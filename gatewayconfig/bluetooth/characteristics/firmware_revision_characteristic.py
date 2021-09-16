import os

from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.logger import get_logger
import gatewayconfig.constants as constants

logger = get_logger(__name__)


class FirmwareRevisionCharacteristic(Characteristic):
    def __init__(self, service):
        Characteristic.__init__(
                self, constants.FIRMWARE_REVISION_CHARACTERISTIC_UUID,
                ["read"], service)

    def ReadValue(self, options):
        logger.debug('Read Firmware')
        # Intentionally reading the env variable each time in case it changes over
        # the application's lifetime
        firmware_version = os.getenv('FIRMWARE_VERSION')
        return string_to_dbus_encoded_byte_array(firmware_version)
