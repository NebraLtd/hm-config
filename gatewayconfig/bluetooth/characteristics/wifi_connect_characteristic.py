import dbus

from lib.cputemp.service import Characteristic

from gatewayconfig.logger import logger
from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.bluetooth.descriptors.wifi_connect_descriptor import WifiConnectDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.nmcli_custom as nmcli_custom
import gatewayconfig.protos.wifi_connect_pb2 as wifi_connect_pb2
import gatewayconfig.constants as constants

class WifiConnectCharacteristic(Characteristic):

    def __init__(self, service):
        self.notifying = False
        Characteristic.__init__(
                self, constants.WIFI_CONNECT_CHARACTERISTIC_UUID,
                ["read", "write", "notify"], service)
        self.add_descriptor(WifiConnectDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))
        self.wifi_status = ""

    def WiFiConnectCallback(self):
        if self.notifying:
            logger.debug('Callback WiFi Connect')
            value = []
            self.wifi_status = "timeout"

            for c in self.wifi_status:
                value.append(dbus.Byte(c.encode()))
            self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):

        logger.debug('Notify WiFi Connect')
        if self.notifying:
            return

        self.notifying = True

        value = []
        self.wifi_status = self.check_wifi_status()
        for c in self.wifi_status:
            value.append(dbus.Byte(c.encode()))
        self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(30000, self.WiFiConnectCallback)

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logger.debug("Write WiFi Connect %s" % value)
        if(self.check_wifi_status() == "connected"):
            nmcli_custom.device.disconnect('wlan0')
            logger.debug('Disconnected From Wifi')

        wifi_details = wifi_connect_pb2.wifi_connect_v1()
        wifi_details.ParseFromString(bytes(value))
        self.wifi_status = "already"
        logger.debug(str(wifi_details.service))

        nmcli_custom.device.wifi_connect(str(wifi_details.service),
                                  str(wifi_details.password))
        self.wifi_status = self.check_wifi_status()

    def check_wifi_status(self):
        # Check the current wi-fi connection status
        logger.debug('Check WiFi Connect')
        state = str(nmcli_custom.device.show('wlan0')['GENERAL.STATE'].split(" ")[0])
        wifi_status = constants.WIFI_STATUSES[state]
        logger.debug("Wifi status is %s" % str(wifi_status))
        return wifi_status

    def ReadValue(self, options):

        logger.debug('Read WiFi Connect')
        self.wifi_status = self.check_wifi_status()
        return string_to_dbus_encoded_byte_array(self.wifi_status)
