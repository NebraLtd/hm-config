import dbus
from time import sleep

from lib.cputemp.service import Characteristic

from gatewayconfig.logger import get_logger
from gatewayconfig.helpers import string_to_dbus_byte_array
from gatewayconfig.bluetooth.descriptors.diagnostics_descriptor import DiagnosticsDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.nmcli_custom as nmcli_custom
import gatewayconfig.protos.diagnostics_pb2 as diagnostics_pb2
import gatewayconfig.constants as constants

DBUS_UNAVAILABLE_VALUE = "Loading..."
DBUS_LOAD_SLEEP_SECONDS = 0.1
logger = get_logger(__name__)


class DiagnosticsCharacteristic(Characteristic):
    # Returns proto of eth, wifi, fw, ip, p2pstatus

    def __init__(self, service, eth0_mac_address, wlan0_mac_address, firmware_version):
        Characteristic.__init__(
                self, constants.DIAGNOSTICS_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(DiagnosticsDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))

        self.new_diagnostics_proto(eth0_mac_address.replace(":", ""),
                                   wlan0_mac_address.replace(":", ""),
                                   firmware_version)

    def ReadValue(self, options):
        logger.debug('Read diagnostics')
        try:
            p2pstatus = self.get_p2pstatus()

            # Update self.diagnostics_proto
            self.update_diagnostics_proto(p2pstatus)
        except Exception as ex:
            logger.exception("Unexpected exception while trying to read diagnostics: %s" % str(ex))

        diagnostics = self.diagnostics_proto.SerializeToString()
        logger.debug("Diagnostics are %s" % diagnostics)
        return string_to_dbus_byte_array(diagnostics)

    # Make a new diagnostics_pb2.diagnostics_v1
    def new_diagnostics_proto(self,
                              eth0_mac_address,
                              wlan0_mac_address,
                              firmware_version):
        logger.debug('New Diagnostics Proto')

        self.diagnostics_proto = diagnostics_pb2.diagnostics_v1()
        self.diagnostics_proto.diagnostics['connected'] = DBUS_UNAVAILABLE_VALUE
        self.diagnostics_proto.diagnostics['dialable'] = DBUS_UNAVAILABLE_VALUE
        self.diagnostics_proto.diagnostics['height'] = DBUS_UNAVAILABLE_VALUE
        self.diagnostics_proto.diagnostics['nat_type'] = DBUS_UNAVAILABLE_VALUE

        self.diagnostics_proto.diagnostics['eth'] = str(eth0_mac_address)
        self.diagnostics_proto.diagnostics['wifi'] = str(wlan0_mac_address)
        self.diagnostics_proto.diagnostics['fw'] = str(firmware_version)
        self.diagnostics_proto.diagnostics['ip'] = ""

    # Update diagnostics_proto member variable
    def update_diagnostics_proto(self, p2pstatus):
        logger.debug('Update Diagnostics Proto')

        if p2pstatus:
            try:
                self.diagnostics_proto.diagnostics['connected'] = str(p2pstatus[0][1])
                self.diagnostics_proto.diagnostics['dialable'] = str(p2pstatus[1][1])
                self.diagnostics_proto.diagnostics['height'] = str(p2pstatus[3][1])
                self.diagnostics_proto.diagnostics['nat_type'] = str(p2pstatus[2][1])
            except Exception as ex:
                logger.exception("Unexpected exception while trying to read p2pstatus")
                raise ex

        self.diagnostics_proto.diagnostics['ip'] = self.get_ip()

    # Returns the p2pstatus or an empty string if there is a dbus failure
    def get_p2pstatus(self):
        logger.debug('Diagnostics miner_bus')
        miner_bus = dbus.SessionBus()
        logger.debug('Diagnostics miner_object')
        miner_object = miner_bus.get_object('com.helium.Miner', '/')
        sleep(DBUS_LOAD_SLEEP_SECONDS)
        logger.debug('Diagnostics miner_interface')
        miner_interface = dbus.Interface(miner_object, 'com.helium.Miner')
        sleep(DBUS_LOAD_SLEEP_SECONDS)
        logger.debug('Diagnostics p2pstatus')

        try:
            p2pstatus = miner_interface.P2PStatus()
            logger.debug('DBUS P2P SUCCEED')
            logger.debug(p2pstatus)
        except dbus.exceptions.DBusException as ex:
            p2pstatus = False
            logger.warn('DBUS P2P FAIL')
            raise ex

        logger.debug("p2pstatus: %s" % p2pstatus)
        return p2pstatus

    # Return the ETH IP address, or WLAN if it does not exist
    # 0.0.0.0 is the default value if neither ETH or WLAN IP available
    def get_ip(self):
        try:
            eth_ip = nmcli_custom.device.show('eth0')['IP4.ADDRESS[1]'][:-3]
        except KeyError:
            pass
        try:
            wlan_ip = nmcli_custom.device.show('wlan0')['IP4.ADDRESS[1]'][:-3]
        except KeyError:
            pass

        ip_address = ""
        if('eth_ip' in locals()):
            logger.debug("Using ETH IP address %s" % eth_ip)
            ip_address = str(eth_ip)
        elif('wlan_ip' in locals()):
            ip_address = str(wlan_ip)
            logger.debug("Using WLAN IP address %s" % wlan_ip)
        return ip_address
