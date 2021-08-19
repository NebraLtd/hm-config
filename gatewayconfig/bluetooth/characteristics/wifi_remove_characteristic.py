
import logging
import dbus

from lib.cputemp.service import Characteristic
import gatewayconfig.protos as protos

from gatewayconfig.bluetooth.descriptors.wifi_remove_descriptor import WifiRemoveDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.nmcli_custom as nmcli_custom
import gatewayconfig.constants as constants

class WifiRemoveCharacteristic(Characteristic):

    def __init__(self, service):
        self.notifying = False
        Characteristic.__init__(
                self, constants.WIFI_REMOVE_CHARACTERISTIC_UUID,
                ["read", "write", "notify"], service)
        self.add_descriptor(WifiRemoveDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))
        self.wifistatus = "False"

    def WiFiRemoveCallback(self):
        if self.notifying:
            logging.debug('Callback WiFi Remove')
            value = []
            val = self.wifistatus

            for c in val:
                value.append(dbus.Byte(c.encode()))
            self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):

        logging.debug('Notify WiFi Remove')
        if self.notifying:
            return

        self.notifying = True

        value = []

        for c in self.WiFiStatus:
            value.append(dbus.Byte(c.encode()))
        self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(30000, self.WiFiRemoveCallback)

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logging.debug('Write WiFi Remove')
        wifiRemoveSSID = protos.wifi_remove_pb2.wifi_remove_v1()
        wifiRemoveSSID.ParseFromString(bytes(value))
        nmcli_custom.connection.delete(wifiRemoveSSID.service)
        logging.debug('Connection %s should be deleted'
                      % wifiRemoveSSID.service)

    def ReadValue(self, options):
        logging.debug('Read WiFi Renove')

        value = []
        val = self.wifistatus
        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value