from lib.cputemp.service import Descriptor
from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
import gatewayconfig.constants as constants


class OnboardingKeyDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, constants.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)
        self.onboarding_key_label = constants.ONBOARDING_KEY_LABEL

    def ReadValue(self, options):
        return string_to_dbus_encoded_byte_array(self.onboarding_key_label)
