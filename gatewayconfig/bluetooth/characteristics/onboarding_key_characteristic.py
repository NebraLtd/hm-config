from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.logger import get_logger
from gatewayconfig.bluetooth.descriptors.onboarding_key_descriptor import OnboardingKeyDescriptor
from gatewayconfig.bluetooth.descriptors.utf8_format_descriptor import UTF8FormatDescriptor
import gatewayconfig.constants as constants

logger = get_logger(__name__)


class OnboardingKeyCharacteristic(Characteristic):
    def __init__(self, service, shared_state):
        Characteristic.__init__(
                self, constants.ONBOARDING_KEY_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(OnboardingKeyDescriptor(self))
        self.add_descriptor(UTF8FormatDescriptor(self))
        self.shared_state = shared_state

    def ReadValue(self, options):
        logger.debug("Read Onboarding Key")
        # Onboarding key is always identical to public key
        self.shared_state.load_public_key()
        logger.debug("Onboarding key:  %s" % self.shared_state.public_key)
        return string_to_dbus_encoded_byte_array(self.shared_state.public_key)
