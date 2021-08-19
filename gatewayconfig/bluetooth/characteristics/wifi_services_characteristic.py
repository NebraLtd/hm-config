
import logging
import dbus

from lib.cputemp.service import Characteristic
import gatewayconfig.protos as protos

from gatewayconfig.bluetooth.descriptors.wifi_services_descriptor import WifiServicesDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.constants as constants

class WifiServicesCharacteristic(Characteristic):

    global wifiCache

    def __init__(self, service):
        Characteristic.__init__(
                self, constants.WIFI_SERVICES_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(WifiServicesDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))

    def ReadValue(self, options):
        logging.debug('Read WiFi Services')
        wifiSsids = protos.wifi_services_pb2.wifi_services_v1()

        for network in wifiCache:
            ssidStr = str(network.ssid)
            if(ssidStr != "--" and ssidStr != ""):
                if(ssidStr not in wifiSsids.services):
                    wifiSsids.services.append(ssidStr)
                    logging.debug(ssidStr)
        value = []
        val = wifiSsids.SerializeToString()

        for c in val:
            value.append(dbus.Byte(c))
        if("offset" in options):
            cutDownArray = value[int(options["offset"]):]
            return cutDownArray
        else:
            return value