
import logging
import dbus

from lib.cputemp.service import Characteristic

from gatewayconfig.bluetooth.descriptors.public_key_descriptor import PublicKeyDescriptor
from gatewayconfig.bluetooth.descriptors.utf8_format_descriptor import UTF8FormatDescriptor
import gatewayconfig.constants as constants

class PublicKeyCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, constants.PUBLIC_KEY_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(PublicKeyDescriptor(self))
        self.add_descriptor(UTF8FormatDescriptor(self))

    def ReadValue(self, options):
        logging.debug('Read Public Key')
        value = []
        val = pubKey
        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value
