import logging
import dbus

from lib.cputemp.service import Characteristic

import gatewayconfig.constants as constants

class ManufacturerNameCharacteristic(Characteristic):
    def __init__(self, service):
        Characteristic.__init__(
                self, constants.MANUFACTURE_NAME_CHARACTERISTIC_UUID,
                ["read"], service)

    def ReadValue(self, options):
        logging.debug('Read Manufacturer')
        value = []
        val = "Nebra LTD."
        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value
