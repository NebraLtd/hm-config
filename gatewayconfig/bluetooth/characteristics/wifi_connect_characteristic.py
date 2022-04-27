import threading
from time import sleep

from lib.cputemp.service import Characteristic

from gatewayconfig.logger import get_logger
from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.bluetooth.descriptors.wifi_connect_descriptor import WifiConnectDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import lib.nmcli_custom as nmcli_custom
import gatewayconfig.protos.wifi_connect_pb2 as wifi_connect_pb2
import gatewayconfig.constants as constants

logger = get_logger(__name__)

NOTIFY_TIMEOUT = 1000   # 1 second


class CommandThread(threading.Thread):
    def __init__(self, chrc):
        super().__init__()
        self.daemon = True
        self.chrc = chrc

    def run(self):
        if self.chrc.wifi_service and self.chrc.wifi_password:
            try:
                sleep(3)
                self.chrc.connect_to_wifi(self.chrc.wifi_service, self.chrc.wifi_password)
            except Exception as e:
                logger.exception("Wifi connect failed: %s" % str(e))

            # wipe out the wifi details
            self.chrc.wifi_service = ""
            self.chrc.wifi_password = ""  # nosec B105

            # Notify wifi status
            wifi_status = self.chrc.check_wifi_status()
            value = string_to_dbus_encoded_byte_array(wifi_status)
            self.chrc.PropertiesChanged(constants.GATT_CHRC_IFACE,
                                        {"Value": value}, [])


class WifiConnectCharacteristic(Characteristic):

    def __init__(self, service):
        self.notifying = False
        self.connecting = True
        Characteristic.__init__(
                self, constants.WIFI_CONNECT_CHARACTERISTIC_UUID,
                ["read", "write", "notify"], service)
        self.add_descriptor(WifiConnectDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))

        # Credential to connect to a WiFi
        self.wifi_service = ""
        self.wifi_password = ""  # nosec B105

    def check_wifi_status(self):
        # Check the current wi-fi connection status
        logger.debug('Check WiFi Connect')

        if self.connecting:
            wifi_status = constants.WIFI_CONNECTING
        else:
            # Convert nmcli device state into bluetooth response
            try:
                nmcli_devices = nmcli_custom.device.status()
                wifi_device = next(filter(lambda x: x.device_type == 'wifi', nmcli_devices))
                if wifi_device.state == 'connected':
                    wifi_status = constants.WIFI_CONNECTED
                else:
                    wifi_status = constants.WIFI_INVALID_PASSWORD
            except Exception as e:
                logger.exception("Getting wifi connection status failed for unknown reason: %s" % str(e))
                wifi_status = constants.WIFI_ERROR

        logger.debug("Wifi status is %s" % wifi_status)
        return wifi_status

    def connect_to_wifi(self, wifi_service, wifi_password):
        logger.debug('Connect to WiFi')
        nmcli_custom.device.wifi_connect(wifi_service, wifi_password)

        # Connecting to the Wifi is finished
        self.connecting = False

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

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logger.debug("Write WiFi Connect %s" % value)

        wifi_details = wifi_connect_pb2.wifi_connect_v1()
        wifi_details.ParseFromString(bytes(value))

        logger.debug(str(wifi_details.service))

        self.wifi_service = str(wifi_details.service)
        self.wifi_password = str(wifi_details.password)

        if self.wifi_service and self.wifi_password:
            # Start connecting to the Wifi
            self.connecting = True

            try:
                cmd_thread = CommandThread(self)
                cmd_thread.start()
            except Exception as ex:
                print(str(ex))

    def ReadValue(self, options):
        logger.debug('Read WiFi Connect')

        wifi_status = self.check_wifi_status()
        return string_to_dbus_encoded_byte_array(wifi_status)
