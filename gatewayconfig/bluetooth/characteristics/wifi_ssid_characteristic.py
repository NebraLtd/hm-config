
import logging
import dbus

from lib.cputemp.service import Characteristic
import gatewayconfig.protos as protos

from gatewayconfig.bluetooth.descriptors.wifi_ssid_descriptor import WifiSSIDDescriptor
from gatewayconfig.bluetooth.descriptors.utf8_format_descriptor import UTF8FormatDescriptor
import gatewayconfig.constants as constants

class WifiSSIDCharacteristic(Characteristic):

    global wifiCache

    def __init__(self, service):
        Characteristic.__init__(
                self, constants.WIFI_SSID_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(WifiSSIDDescriptor(self))
        self.add_descriptor(UTF8FormatDescriptor(self))

    def ReadValue(self, options):

        logging.debug('Read WiFi SSID')
        activeConnection = ""
        for network in wifiCache:
            if(network.ssid != "--"):
                if(network.in_use):
                    activeConnection = str(network.ssid)
                    print(activeConnection)
        value = []

        for c in activeConnection:
            value.append(dbus.Byte(c.encode()))
        return value
