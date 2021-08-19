import logging
import dbus

from lib.cputemp.service import Characteristic
import gatewayconfig.protos as protos

from gatewayconfig.bluetooth.descriptors.wifi_connect_descriptor import WifiConnectDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.nmcli_custom as nmcli_custom
import gatewayconfig.constants as constants

class WifiConnectCharacteristic(Characteristic):

    def __init__(self, service):
        self.notifying = False
        Characteristic.__init__(
                self, constants.WIFI_CONNECT_CHARACTERISTIC_UUID,
                ["read", "write", "notify"], service)
        self.add_descriptor(WifiConnectDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))
        self.WiFiStatus = ""

    def WiFiConnectCallback(self):
        if self.notifying:
            logging.debug('Callback WiFi Connect')
            value = []
            self.WiFiStatus = "timeout"

            for c in self.WiFiStatus:
                value.append(dbus.Byte(c.encode()))
            self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):

        logging.debug('Notify WiFi Connect')
        if self.notifying:
            return

        self.notifying = True

        value = []
        self.WiFiStatus = self.checkWiFIStatus()
        for c in self.WiFiStatus:
            value.append(dbus.Byte(c.encode()))
        self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(30000, self.WiFiConnectCallback)

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logging.debug('Write WiFi Connect')
        if(self.checkWiFIStatus() == "connected"):
            nmcli_custom.device.disconnect('wlan0')
            logging.debug('Disconnected From Wifi')
        # logging.debug(value)
        wiFiDetails = protos.wifi_connect_pb2.wifi_connect_v1()
        # logging.debug('PB2C')
        wiFiDetails.ParseFromString(bytes(value))
        # logging.debug('PB2P')
        self.WiFiStatus = "already"
        logging.debug(str(wiFiDetails.service))

        nmcli_custom.device.wifi_connect(str(wiFiDetails.service),
                                  str(wiFiDetails.password))
        self.WiFiStatus = self.checkWiFIStatus()

    def checkWiFIStatus(self):
        # Check the current wi-fi connection status
        logging.debug('Check WiFi Connect')
        state = str(nmcli_custom.device.show('wlan0')['GENERAL.STATE'].split(" ")[0])
        logging.debug(str(constants.wifiStatus[state]))
        return constants.wifiStatus[state]

    def ReadValue(self, options):

        logging.debug('Read WiFi Connect')
        self.WiFiStatus = self.checkWiFIStatus()
        value = []

        for c in self.WiFiStatus:
            value.append(dbus.Byte(c.encode()))
        return value