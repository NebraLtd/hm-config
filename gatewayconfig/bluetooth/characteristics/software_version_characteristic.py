
import logging
import dbus
import os

from lib.cputemp.service import Characteristic

import gatewayconfig.constants as constants

class SoftwareVersionCharacteristic(Characteristic):
    def __init__(self, service):
        Characteristic.__init__(
                self, constants.SOFTWARE_VERSION_CHARACTERISTIC_UUID,
                ["read"], service)

    def ReadValue(self, options):
        logging.debug('Read Firmware')

        val = os.getenv('FIRMWARE_VERSION')

        value = []

        for c in val:
            value.append(dbus.Byte(c.encode()))

        return value