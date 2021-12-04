from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.logger import get_logger
from gatewayconfig.bluetooth.descriptors.lights_descriptor import LightsDescriptor
from gatewayconfig.bluetooth.descriptors.utf8_format_descriptor import UTF8FormatDescriptor
import gatewayconfig.constants as constants

logger = get_logger(__name__)
DEFAULT_LIGHTS_VALUE = 'false'


class LightsCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, constants.LIGHTS_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(LightsDescriptor(self))
        self.add_descriptor(UTF8FormatDescriptor(self))

    def ReadValue(self, options):
        logger.debug('Read Lights')
        return string_to_dbus_encoded_byte_array(DEFAULT_LIGHTS_VALUE)
