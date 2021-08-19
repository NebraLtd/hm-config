import logging
import dbus

from lib.cputemp.service import Characteristic

from gatewayconfig.bluetooth.descriptors.lights_descriptor import LightsDescriptor
from gatewayconfig.bluetooth.descriptors.utf8_format_descriptor import UTF8FormatDescriptor
import gatewayconfig.constants as constants

class LightsCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, constants.LIGHTS_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(LightsDescriptor(self))
        self.add_descriptor(UTF8FormatDescriptor(self))

    def ReadValue(self, options):
        logging.debug('Read Lights')
        value = []
        val = "false"

        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value