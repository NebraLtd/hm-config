from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.logger import logger
from gatewayconfig.bluetooth.descriptors.onboarding_key_descriptor import OnboardingKeyDescriptor
from gatewayconfig.bluetooth.descriptors.utf8_format_descriptor import UTF8FormatDescriptor
import gatewayconfig.constants as constants

class OnboardingKeyCharacteristic(Characteristic):
    def __init__(self, service, onboarding_key):
        Characteristic.__init__(
                self, constants.ONBOARDING_KEY_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(OnboardingKeyDescriptor(self))
        self.add_descriptor(UTF8FormatDescriptor(self))
        self.onboarding_key = onboarding_key

    def ReadValue(self, options):
        logger.debug("Read Onboarding Key")
        logger.debug("Onboarding key:  %s" % self.onboarding_key)
        return string_to_dbus_encoded_byte_array(self.onboarding_key)
