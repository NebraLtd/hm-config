import logging
import dbus
from time import sleep

from lib.cputemp.service import Characteristic
import gatewayconfig.protos.add_gateway_pb2 as add_gateway_pb2

from gatewayconfig.bluetooth.descriptors.add_gateway_descriptor import AddGatewayDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.constants as constants

class AddGatewayCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, constants.ADD_GATEWAY_CHARACTERISTIC_UUID,
                ["read", "write", "notify"], service)
        self.add_descriptor(AddGatewayDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))
        self.notifyValue = []
        for c in "init":
            self.notifyValue.append(dbus.Byte(c.encode()))

    def AddGatewayCallback(self):
        if self.notifying:
            logging.debug('Callback Add Gateway')
            # value = []
            # val = ""

            # for c in val:
            #    value.append(dbus.Byte(c.encode()))
            self.PropertiesChanged(constants.GATT_CHRC_IFACE,
                                   {"Value": self.notifyValue}, [])

    def StartNotify(self):

        logging.debug('Notify Add Gateway')
        if self.notifying:
            return

        self.notifying = True

        self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": self.notifyValue},
                               [])
        self.add_timeout(30000, self.AddGatewayCallback)

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logging.debug('Write Add Gateway')
        waitVal = []
        for c in "wait":
            waitVal.append(dbus.Byte(c.encode()))
        self.notifyValue = waitVal

        # logging.debug(value)
        addGatewayDetails = add_gateway_pb2.add_gateway_v1()
        # logging.debug('PB2C')
        addGatewayDetails.ParseFromString(bytes(value))
        # logging.debug('PB2P')
        # logging.debug(str(addGatewayDetails))
        miner_bus = dbus.SystemBus()
        miner_object = miner_bus.get_object('com.helium.Miner', '/')
        sleep(0.05)
        miner_interface = dbus.Interface(miner_object, 'com.helium.Miner')
        sleep(0.05)
        addMinerRequest = \
            miner_interface. \
            AddGateway(addGatewayDetails.owner, addGatewayDetails.fee,
                       addGatewayDetails.amount, addGatewayDetails.payer)
        # logging.debug(addMinerRequest)
        logging.debug("Adding Response")
        self.notifyValue = addMinerRequest

    def ReadValue(self, options):
        logging.debug('Read Add Gateway')
        if("offset" in options):
            cutDownArray = self.notifyValue[int(options["offset"]):]
            return cutDownArray
        else:
            return self.notifyValue
        # logging.debug(self.notifyValue)
