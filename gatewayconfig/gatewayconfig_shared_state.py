import json
import threading

from hm_pyhelper.miner_param import get_public_keys_rust
from hm_pyhelper.logger import get_logger


LOGGER = get_logger(__name__)
PUBLIC_KEY_UNAVAILABLE = 'Unavailable'


# Context is shared between multiple threads/processes.
# This class simplifies and centralizes read/write of the state:
class GatewayconfigSharedState:

    def __init__(self):
        self.should_scan_wifi = False
        self.is_advertising_bluetooth = False
        self.are_diagnostics_ok = False
        self.public_key = PUBLIC_KEY_UNAVAILABLE
        self.should_advertise_bluetooth_condition_event = threading.Event()
        self.should_advertise_bluetooth_condition_event.set()

    def to_s(self):
        serial_dict = self.__dict__.copy()
        cv_event = self.should_advertise_bluetooth_condition_event.is_set()
        serial_dict['should_advertise_bluetooth_condition_event'] = cv_event
        return json.dumps(serial_dict)

    def load_public_key(self):
        """
        Attempt to retrieve the public key unless it has already
        completed successfully. Keys are never expected to update.
        """
        if self.public_key != PUBLIC_KEY_UNAVAILABLE:
            return

        try:
            public_keys = get_public_keys_rust()
            self.public_key = public_keys['key']
        except Exception:
            LOGGER.exception("Unable to read public key.")
