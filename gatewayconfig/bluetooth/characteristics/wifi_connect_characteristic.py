from lib.cputemp.service import Characteristic

from gatewayconfig.logger import get_logger
from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.bluetooth.descriptors.wifi_connect_descriptor import WifiConnectDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.nmcli_custom as nmcli_custom
import gatewayconfig.protos.wifi_connect_pb2 as wifi_connect_pb2
import gatewayconfig.constants as constants

logger = get_logger(__name__)

NOTIFY_TIMEOUT = 60


class WifiConnectCharacteristic(Characteristic):

    def __init__(self, service):
        self.notifying = False
        Characteristic.__init__(
                self, constants.WIFI_CONNECT_CHARACTERISTIC_UUID,
                ["read", "write", "notify"], service)
        self.add_descriptor(WifiConnectDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))

        # Credential to connect to a WiFi
        self.wifi_service = ""
        self.wifi_password = ""

    def check_wifi_status(self):
        # Check the current wi-fi connection status
        logger.debug('Check WiFi Connect')
        nm_state = str(nmcli_custom.device.show('wlan0')['GENERAL.STATE'].split(" ")[0])

        # Convert the network manager device state into wifi status response
        wifi_status = constants.WIFI_STATUSES.get(nm_state,
                                                  constants.WIFI_ERROR)
        logger.debug("Wifi status is %s" % wifi_status)

        return wifi_status

    def connect_to_wifi(self, wifi_service, wifi_password):
        logger.debug('Connect to WiFi')
        if self.check_wifi_status() == constants.WIFI_CONNECTED:
            nmcli_custom.device.disconnect('wlan0')
            logger.debug('Disconnected From WiFi')

        nmcli_custom.device.wifi_connect(wifi_service, wifi_password)

    def connect_to_wifi_timeout(self):
        if self.notifying:
            logger.debug('Connect to WiFi Timeout')

            # Notify wifi status
            wifi_status = self.check_wifi_status()
            value = string_to_dbus_encoded_byte_array(wifi_status)
            self.PropertiesChanged(constants.GATT_CHRC_IFACE,
                                   {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        logger.debug('Notify WiFi Connect')
        if self.notifying:
            return

        self.notifying = True

        self.add_timeout(NOTIFY_TIMEOUT, self.connect_to_wifi_timeout)

        if self.wifi_service and self.wifi_password:
            try:
                self.connect_to_wifi(self.wifi_service, self.wifi_password)
            except Exception:
                logger.exception("Wifi connect failed for unknown reason")

            # Notify wifi status
            wifi_status = self.check_wifi_status()
            value = string_to_dbus_encoded_byte_array(wifi_status)
            self.PropertiesChanged(constants.GATT_CHRC_IFACE,
                                   {"Value": value}, [])

            # wipe out the wifi details
            self.wifi_service = ""
            self.wifi_password = ""

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logger.debug("Write WiFi Connect %s" % value)

        wifi_details = wifi_connect_pb2.wifi_connect_v1()
        wifi_details.ParseFromString(bytes(value))

        logger.debug(str(wifi_details.service))

        self.wifi_service = str(wifi_details.service)
        self.wifi_password = str(wifi_details.password)

    def ReadValue(self, options):
        logger.debug('Read WiFi Connect')

        wifi_status = self.check_wifi_status()
        return string_to_dbus_encoded_byte_array(wifi_status)
