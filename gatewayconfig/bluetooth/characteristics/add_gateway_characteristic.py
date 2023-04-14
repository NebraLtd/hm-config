from lib.cputemp.service import Characteristic

from gatewayconfig.logger import get_logger
from gatewayconfig.helpers import string_to_dbus_encoded_byte_array, string_to_dbus_byte_array
from gatewayconfig.bluetooth.descriptors.add_gateway_descriptor import AddGatewayDescriptor
from gatewayconfig.bluetooth.descriptors.opaque_structure_descriptor import OpaqueStructureDescriptor
import gatewayconfig.protos.add_gateway_pb2 as add_gateway_pb2
import gatewayconfig.constants as constants
from hm_pyhelper.gateway_grpc.client import GatewayClient
import grpc

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
        self.add_gateway_details = None

    # helium's ble response parsing for create gateway txn
    # counts anything more than 20 chars as a valid transaction
    def _limit_error_chars(self, error_string: str) -> bytes:
        return error_string[:18].encode()

    def create_add_gateway_txn(self) -> object:
        """
        returns grpc return value if successful, None otherwise
        """
        if not self.add_gateway_details:
            return None

        try:
            with GatewayClient() as client:
                transaction = client.create_add_gateway_txn(
                            owner_address=self.add_gateway_details.owner,
                            payer_address=self.add_gateway_details.payer
                        )
                return transaction
        except grpc.RpcError as err:
            logger.error(f"rpc error: {err}")
            return self._limit_error_chars(f"g-error: {err}")
        except Exception as err:
            logger.error(err)
            return self._limit_error_chars(f"g-error: {err}")

    # def AddGatewayCallback(self):
    #     if self.notifying:
    #         logger.debug('Callback Add Gateway')
    #         self.PropertiesChanged(constants.GATT_CHRC_IFACE,
    #                                {"Value": self.notifyValue}, [])

    def StartNotify(self):
        logger.debug('Notify Add Gateway')
        if self.notifying:
            return

        self.notifying = True

        self.PropertiesChanged(constants.GATT_CHRC_IFACE, {"Value": self.notifyValue},
                               [])
        # self.add_timeout(30000, self.AddGatewayCallback)

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logger.debug('Write Add Gateway')
        try:
            self.notifyValue = string_to_dbus_encoded_byte_array("wait")

            addGatewayDetails = add_gateway_pb2.add_gateway_v1()
            addGatewayDetails.ParseFromString(bytes(value))

            logger.debug(f"add gateway owner {addGatewayDetails.owner}, fee {addGatewayDetails.fee} "
                         f"amount {addGatewayDetails.amount}, payer {addGatewayDetails.payer}")
            self.add_gateway_details = addGatewayDetails
            # some thought was given to whether to start the grpc call straight away in a thread/process
            # and read value from it in readValue. But write and read will come over bluetooth almost back
            # back. Don't see much value in extra complexity.
        except Exception:
            logger.exception("Unable to register gateway for unknown reason")

    def ReadValue(self, options):
        logger.debug('Read Add Gateway')
        value = self.create_add_gateway_txn()
        self.notifyValue = string_to_dbus_byte_array(value)
        if "offset" in options:
            logger.debug("fishy: offset demanded from add gateway transaction array")
            cutDownArray = self.notifyValue[int(options["offset"]):]
            return cutDownArray
        else:
            return self.notifyValue
