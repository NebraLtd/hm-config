import dbus
import os

from lib.cputemp.service import Characteristic

from gatewayconfig.logger import logger
from gatewayconfig.helpers import string_to_dbus_byte_array
from gatewayconfig.bluetooth.descriptors.diagnostics_descriptor import DiagnosticsDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.nmcli_custom as nmcli_custom
import gatewayconfig.protos.diagnostics_pb2 as diagnostics_pb2
import gatewayconfig.constants as constants

DBUS_UNAVAILABLE_VALUE = "Loading..."

class DiagnosticsCharacteristic(Characteristic):
    # Returns proto of eth, wifi, fw, ip, p2pstatus

    def __init__(self, service, eth0_mac_address, wlan0_mac_address):
        Characteristic.__init__(
                self, constants.DIAGNOSTICS_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(DiagnosticsDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))
        self.p2pstatus = False
        self.eth0_mac_address = eth0_mac_address
        self.wlan0_mac_address = wlan0_mac_address

    def ReadValue(self, options):
        logger.debug('Read diagnostics')
        try:
            self.p2pstatus = self.get_p2pstatus()
            diagnostics = self.build_diagnostics_proto().SerializeToString()
            logger.debug("Diagnostics are %s" % diagnostics)
            return string_to_dbus_byte_array(diagnostics)
        except Exception:
            logger.exception("Unexpected exception while trying to read diagnostics")

    # Returns the p2pstatus or an empty string if there is a dbus failure
    def get_p2pstatus(self):
        logger.debug('Diagnostics miner_bus')
        miner_bus = dbus.SystemBus()
        logger.debug('Diagnostics miner_object')
        miner_object = miner_bus.get_object('com.helium.Miner', '/')
        logger.debug('Diagnostics miner_interface')
        miner_interface = dbus.Interface(miner_object, 'com.helium.Miner')
        logger.debug('Diagnostics p2pstatus')
            
        try:
            p2pstatus = miner_interface.P2PStatus()
            logger.debug('DBUS P2P SUCCEED')
            logger.debug(self.p2pstatus)
        except dbus.exceptions.DBusException:
            p2pstatus = False
            logger.warn('DBUS P2P FAIL')

        logger.debug("p2pstatus: %s" % p2pstatus)
        return p2pstatus

    # Returns a diagnostics_pb2.diagnostics_v1
    def build_diagnostics_proto(self):
        diagnostics_proto = diagnostics_pb2.diagnostics_v1()
        if not self.p2pstatus:
            diagnostics_proto.diagnostics['connected'] = DBUS_UNAVAILABLE_VALUE
            diagnostics_proto.diagnostics['dialable'] = DBUS_UNAVAILABLE_VALUE
            diagnostics_proto.diagnostics['height'] = DBUS_UNAVAILABLE_VALUE
            diagnostics_proto.diagnostics['nat_type'] = DBUS_UNAVAILABLE_VALUE
        else:
            diagnostics_proto.diagnostics['connected'] = str(self.p2pstatus[0][1])
            diagnostics_proto.diagnostics['dialable'] = str(self.p2pstatus[1][1])
            diagnostics_proto.diagnostics['height'] = str(self.p2pstatus[3][1])
            diagnostics_proto.diagnostics['nat_type'] = str(self.p2pstatus[2][1])

        diagnostics_proto.diagnostics['eth'] = self.eth0_mac_address.replace(":", "")
        diagnostics_proto.diagnostics['wifi'] = self.wlan0_mac_address.replace(":", "")
        diagnostics_proto.diagnostics['fw'] = os.getenv('FIRMWARE_VERSION')
        diagnostics_proto.diagnostics['ip'] = self.get_ip()
        logger.debug('All attibutes were added to the diagnostics proto')
        return diagnostics_proto
    
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

        ip_address = "0.0.0.0"  # nosec
        if('eth_ip' in locals()):
            logger.debug("Using ETH IP address %s" % eth_ip)
            ip_address = str(eth_ip)
        elif('wlanIP' in locals()):
            ip_address = str(wlan_ip)
            logger.debug("Using WLAN IP address %s" % wlan_ip)
        return ip_address

