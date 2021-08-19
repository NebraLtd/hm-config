import logging
import dbus

from lib.cputemp.service import Characteristic
import gatewayconfig.protos.diagnostics_pb2 as diagnostics_pb2

from gatewayconfig.bluetooth.descriptors.diagnostics_descriptor import DiagnosticsDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.nmcli_custom as nmcli_custom
import gatewayconfig.constants as constants

class DiagnosticsCharacteristic(Characteristic):
    # Returns proto of eth, wifi, fw, ip, p2pstatus

    def __init__(self, service):
        Characteristic.__init__(
                self, constants.DIAGNOSTICS_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(DiagnosticsDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))
        self.p2pstatus = ""

    def ReadValue(self, options): # noqa 901
        # TODO (Rob): come back and make this method less complex for
        # C901 complexity rules.
        logging.debug('Read diagnostics')
        logging.debug('Diagnostics miner_bus')
        miner_bus = dbus.SystemBus()
        logging.debug('Diagnostics miner_object')
        miner_object = miner_bus.get_object('com.helium.Miner', '/')
        logging.debug('Diagnostics miner_interface')
        miner_interface = dbus.Interface(miner_object, 'com.helium.Miner')
        logging.debug('Diagnostics p2pstatus')
        try:
            self.p2pstatus = miner_interface.P2PStatus()
            logging.debug('DBUS P2P SUCCEED')
            logging.debug(self.p2pstatus)
        except dbus.exceptions.DBusException:
            self.p2pstatus = ""
            logging.debug('DBUS P2P FAIL')

        try:
            ethIP = nmcli_custom.device.show('eth0')['IP4.ADDRESS[1]'][:-3]
        except KeyError:
            pass
        try:
            wlanIP = nmcli_custom.device.show('wlan0')['IP4.ADDRESS[1]'][:-3]
        except KeyError:
            pass

        ipAddress = "0.0.0.0"  # nosec
        if('ethIP' in locals()):
            ipAddress = str(ethIP)
        elif('wlanIP' in locals()):
            ipAddress = str(wlanIP)

        diagnosticsProto = diagnostics_pb2.diagnostics_v1()
        diagnosticsProto.diagnostics['connected'] = str(self.p2pstatus[0][1])
        diagnosticsProto.diagnostics['dialable'] = str(self.p2pstatus[1][1])
        diagnosticsProto.diagnostics['height'] = str(self.p2pstatus[3][1])
        diagnosticsProto.diagnostics['nat_type'] = str(self.p2pstatus[2][1])
        try:
            diagnosticsProto.diagnostics['eth'] = \
                open("/sys/class/net/eth0/address").readline(). \
                strip().replace(":", "")
        except FileNotFoundError:
            diagnosticsProto.diagnostics['eth'] = "FF:FF:FF:FF:FF:FF"
        diagnosticsProto.diagnostics['fw'] = os.getenv('FIRMWARE_VERSION')
        diagnosticsProto.diagnostics['ip'] = ipAddress
        try:
            wifi_diag = open("/sys/class/net/wlan0/address").readline(). \
                strip().replace(":", "")
            diagnosticsProto.diagnostics['wifi'] = wifi_diag
        except FileNotFoundError:
            diagnosticsProto.diagnostics['wifi'] = "FF:FF:FF:FF:FF:FF"
        logging.debug('items added to proto')
        value = []
        val = diagnosticsProto.SerializeToString()
        logging.debug(val)
        for c in val:
            value.append(dbus.Byte(c))
        return value
