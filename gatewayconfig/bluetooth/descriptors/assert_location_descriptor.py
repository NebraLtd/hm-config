import dbus
from lib.cputemp.service import Descriptor
import gatewayconfig.constants as constants

class AssertLocationDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, constants.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = constants.ASSERT_LOCATION_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value