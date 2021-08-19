
import logging
import dbus

from lib.cputemp.service import Characteristic

import gatewayconfig.constants as constants

class SerialNumberCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, constants.SERIAL_NUMBER_CHARACTERISTIC_UUID,
                ["read"], service)

    def ReadValue(self, options):
        logging.debug('Read Serial Number')
        value = []
        val = open("/sys/class/net/eth0/address").readline() \
            .strip().replace(":", "")

        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value