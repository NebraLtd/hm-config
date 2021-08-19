import logging
import dbus

from lib.cputemp.service import Characteristic

from gatewayconfig.bluetooth.descriptors.onboarding_key_descriptor import OnboardingKeyDescriptor
from gatewayconfig.bluetooth.descriptors.utf8_format_descriptor import UTF8FormatDescriptor
import gatewayconfig.constants as constants

class OnboardingKeyCharacteristic(Characteristic):
    def __init__(self, service):
        Characteristic.__init__(
                self, constants.ONBOARDING_KEY_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(OnboardingKeyDescriptor(self))
        self.add_descriptor(UTF8FormatDescriptor(self))

    def ReadValue(self, options):
        logging.debug('Read Onboarding Key')
        value = []
        val = onboardingKey

        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value