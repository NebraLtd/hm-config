
import logging
import dbus

from lib.cputemp.service import Characteristic
import gatewayconfig.protos as protos

from gatewayconfig.bluetooth.descriptors.wifi_configured_services_descriptor import WifiConfiguredServicesDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.constants as constants

class WifiConfiguredServicesCharacteristic(Characteristic):

    global wifiCache

    def __init__(self, service):
        Characteristic.__init__(
                self, constants.WIFI_CONFIGURED_SERVICES_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(WifiConfiguredServicesDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))

    def ReadValue(self, options):
        logging.debug('Read WiFi CONFIGURED Services')
        wifiConfigured = protos.wifi_services_pb2.wifi_services_v1()

        for network in wifiCache:
            if(network.ssid != "--"):
                if(network.in_use):
                    activeConnection = str(network.ssid)
                    wifiConfigured.services.append(activeConnection)
                    print(activeConnection)
        value = []
        val = wifiConfigured.SerializeToString()

        for c in val:
            value.append(dbus.Byte(c))

        return value