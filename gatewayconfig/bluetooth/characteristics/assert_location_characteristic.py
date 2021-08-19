import dbus
from time import sleep
import h3
import logging

from lib.cputemp.service import Characteristic
import gatewayconfig.protos.assert_location_pb2 as assert_location_pb2

from gatewayconfig.bluetooth.descriptors.assert_location_descriptor import AssertLocationDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.constants as constants

class AssertLocationCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, constants.ASSERT_LOCATION_CHARACTERISTIC_UUID,
                ["read", "write", "notify"], service)
        self.add_descriptor(AssertLocationDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))
        self.notifyValue = []
        for c in "init":
            self.notifyValue.append(dbus.Byte(c.encode()))

    def AddGatewayCallback(self):
        if self.notifying:
            logging.debug('Callback Assert Location')
            value = []
            val = ""

            for c in val:
                value.append(dbus.Byte(c.encode()))
            self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": value}, [])

    def StartNotify(self):

        logging.debug('Notify Assert Location')
        if self.notifying:
            return

        self.notifying = True

        self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": self.notifyValue},
                               [])
        self.add_timeout(30000, self.AddGatewayCallback)

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logging.debug('Write Assert Location')
        logging.debug(value)
        assLocDet = assert_location_pb2.assert_loc_v1()
        logging.debug('PB2C')
        assLocDet.ParseFromString(bytes(value))
        logging.debug('PB2P')
        logging.debug(str(assLocDet))
        miner_bus = dbus.SystemBus()
        miner_object = miner_bus.get_object('com.helium.Miner', '/')
        sleep(0.05)
        miner_interface = dbus.Interface(miner_object, 'com.helium.Miner')
        sleep(0.05)
        h3String = h3.geo_to_h3(assLocDet.lat, assLocDet.lon, 12)
        # logging.debug(h3String)
        # H3String, Owner, Nonce, Amount, Fee, Paye
        minerAssertRequest = \
            miner_interface. \
            AssertLocation(h3String,
                           assLocDet.owner, assLocDet.nonce, assLocDet.amount,
                           assLocDet.fee, assLocDet.payer)
        # logging.debug(assLocDet)
        self.notifyValue = minerAssertRequest

    def ReadValue(self, options):
        logging.debug('Read Assert Location')
        # logging.debug(options)
        if("offset" in options):
            cutDownArray = self.notifyValue[int(options["offset"]):]
            return cutDownArray
        else:
            return self.notifyValue
