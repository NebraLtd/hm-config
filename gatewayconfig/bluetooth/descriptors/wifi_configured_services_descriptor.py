from lib.cputemp.service import Descriptor
from gatewayconfig.helpers import string_to_dbus_byte_array
import gatewayconfig.constants as constants

class WifiConfiguredServicesDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, constants.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        return string_to_dbus_byte_array(constants.WIFI_CONFIGURED_SERVICES_LABEL)
