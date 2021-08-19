
import logging
import dbus

from lib.cputemp.service import Characteristic

from gatewayconfig.helpers import string_to_dbus_byte_array
from gatewayconfig.logger import logger
from gatewayconfig.bluetooth.descriptors.public_key_descriptor import PublicKeyDescriptor
from gatewayconfig.bluetooth.descriptors.utf8_format_descriptor import UTF8FormatDescriptor
import gatewayconfig.constants as constants

class PublicKeyCharacteristic(Characteristic):

    def __init__(self, service, pub_key):
        Characteristic.__init__(
                self, constants.PUBLIC_KEY_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(PublicKeyDescriptor(self))
        self.add_descriptor(UTF8FormatDescriptor(self))
        self.pub_key = pub_key

    def ReadValue(self, options):
        logger.debug("Read Public Key: %s", self.pub_key)
        return string_to_dbus_byte_array(self.pub_key)