import dbus
from time import sleep
import h3

from lib.cputemp.service import Characteristic

from gatewayconfig.logger import get_logger
from gatewayconfig.helpers import string_to_dbus_encoded_byte_array
from gatewayconfig.bluetooth.descriptors.assert_location_descriptor import AssertLocationDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.protos.assert_location_pb2 as assert_location_pb2
import gatewayconfig.constants as constants

logger = get_logger(__name__)
DBUS_LOAD_SLEEP_SECONDS = 0.1


class AssertLocationCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, constants.ASSERT_LOCATION_CHARACTERISTIC_UUID,
                ["read", "write", "notify"], service)
        self.add_descriptor(AssertLocationDescriptor(self))
        self.add_descriptor(OpaqueStructureDescriptor(self))
        self.notifyValue = string_to_dbus_encoded_byte_array("init")

    def AddGatewayCallback(self):
        if self.notifying:
            logger.debug('Callback Assert Location')
            value = string_to_dbus_encoded_byte_array("")
            self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": value}, [])

    def StartNotify(self):

        logger.debug('Notify Assert Location')
        if self.notifying:
            return

        self.notifying = True

        self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": self.notifyValue},
                               [])
        self.add_timeout(30000, self.AddGatewayCallback)

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logger.debug('Write Assert Location')
        try:
            logger.debug(value)
            assert_location_details = assert_location_pb2.assert_loc_v1()
            logger.debug('PB2C')
            assert_location_details.ParseFromString(bytes(value))
            logger.debug('PB2P')
            logger.debug(str(assert_location_details))

            logger.debug("Loading dbus com.helium.Miner")
            miner_bus = dbus.SessionBus()
            miner_object = miner_bus.get_object('com.helium.Miner', '/')
            sleep(DBUS_LOAD_SLEEP_SECONDS)
            miner_interface = dbus.Interface(miner_object, 'com.helium.Miner')
            sleep(DBUS_LOAD_SLEEP_SECONDS)

            logger.debug("Parsing assert values")
            h3_string = h3.geo_to_h3(assert_location_details.lat, assert_location_details.lon, 12)
            owner = assert_location_details.owner
            nonce = assert_location_details.nonce
            amount = assert_location_details.amount
            fee = assert_location_details.fee
            payer = assert_location_details.payer

            logger.debug("Going to assert location for h3 %s, owner %s, nonce %s, amount %s, fee %s, payer %s" %
                         (h3_string, owner, nonce, amount, fee, payer))

            miner_assert_request = miner_interface.AssertLocation(h3_string, owner, nonce, amount, fee, payer)

            logger.debug("Asserted location")
            self.notifyValue = miner_assert_request
        except Exception:
            logger.exception("Unable to register gateway for unknown reason")

    def ReadValue(self, options):
        logger.debug('Read Assert Location')
        if("offset" in options):
            cutDownArray = self.notifyValue[int(options["offset"]):]
            return cutDownArray
        else:
            return self.notifyValue
