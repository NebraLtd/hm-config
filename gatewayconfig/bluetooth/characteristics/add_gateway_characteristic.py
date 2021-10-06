import dbus
from time import sleep

from lib.cputemp.service import Characteristic

from gatewayconfig.logger import get_logger
from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.bluetooth.descriptors.add_gateway_descriptor import AddGatewayDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.protos.add_gateway_pb2 as add_gateway_pb2
import gatewayconfig.constants as constants

logger = get_logger(__name__)
DBUS_LOAD_SLEEP_SECONDS = 0.1


class AddGatewayCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, constants.ADD_GATEWAY_CHARACTERISTIC_UUID,
                ["read", "write", "notify"], service)
        self.add_descriptor(AddGatewayDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))
        self.notifyValue = string_to_dbus_encoded_byte_array("init")

    def AddGatewayCallback(self):
        if self.notifying:
            logger.debug('Callback Add Gateway')
            self.PropertiesChanged(constants.GATT_CHRC_IFACE,
                                   {"Value": self.notifyValue}, [])

    def StartNotify(self):

        logger.debug('Notify Add Gateway')
        if self.notifying:
            return

        self.notifying = True

        self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": self.notifyValue},
                               [])
        self.add_timeout(30000, self.AddGatewayCallback)

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logger.debug('Write Add Gateway')
        try:
            self.notifyValue = string_to_dbus_encoded_byte_array("wait")

            addGatewayDetails = add_gateway_pb2.add_gateway_v1()
            addGatewayDetails.ParseFromString(bytes(value))
            miner_bus = dbus.SessionBus()

            logger.debug("Loading dbus com.helium.Miner")
            miner_object = miner_bus.get_object('com.helium.Miner', '/')
            sleep(DBUS_LOAD_SLEEP_SECONDS)
            miner_interface = dbus.Interface(miner_object, 'com.helium.Miner')
            sleep(DBUS_LOAD_SLEEP_SECONDS)

            logger.debug("Parsing onboarding values")
            owner = addGatewayDetails.owner
            fee = addGatewayDetails.fee
            amount = addGatewayDetails.amount
            payer = addGatewayDetails.payer

            logger.debug("Registering owner %s, fee %s, amount %s, payer %s" % (owner, fee, amount, payer))
            # Calls https://github.com/helium/miner/blob/e55437beac4b46d15cbd079c9c8df045ffc0bf49/src/miner_ebus.erl#L50
            addMinerRequest = miner_interface.AddGateway(owner, fee, amount, payer)
            logger.debug("Adding Response")
            self.notifyValue = addMinerRequest
        except Exception:
            logger.exception("Unable to register gateway for unknown reason")

    def ReadValue(self, options):
        logger.debug('Read Add Gateway')
        if("offset" in options):
            cutDownArray = self.notifyValue[int(options["offset"]):]
            return cutDownArray
        else:
            return self.notifyValue
