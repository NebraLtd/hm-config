from lib.cputemp.service import Characteristic

from gatewayconfig.logger import get_logger
from gatewayconfig.helpers import string_to_dbus_byte_array
from gatewayconfig.bluetooth.descriptors.diagnostics_descriptor import DiagnosticsDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import lib.nmcli_custom as nmcli_custom
import gatewayconfig.protos.diagnostics_pb2 as diagnostics_pb2
import gatewayconfig.constants as constants

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
            # Update self.diagnostics_proto
            self.update_diagnostics_proto()
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

        self.diagnostics_proto.diagnostics['height'] = "unavailable"

        self.diagnostics_proto.diagnostics['eth'] = str(eth0_mac_address)
        self.diagnostics_proto.diagnostics['wifi'] = str(wlan0_mac_address)
        self.diagnostics_proto.diagnostics['fw'] = str(firmware_version)
        self.diagnostics_proto.diagnostics['ip'] = ""

    # Update diagnostics_proto member variable
    def update_diagnostics_proto(self):
        logger.debug('Update Diagnostics Proto')

        # TODO:: update these two from grpc client
        # height is available and connected might still have some diag value
        # if they gateway-rs reports a valid validator uri, it can be assumed
        # to be connected to blockchain I think
        # self.diagnostics_proto.diagnostics['connected'] = str(p2pstatus[0][1])
        # self.diagnostics_proto.diagnostics['height'] = str(p2pstatus[3][1])

        self.diagnostics_proto.diagnostics['ip'] = self.get_ip()

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
