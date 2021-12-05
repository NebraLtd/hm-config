import json
from hm_pyhelper.miner_param import get_public_keys_rust
from hm_pyhelper.logger import get_logger

LOGGER = get_logger(__name__)
PUBLIC_KEY_UNAVAILABLE = 'Unavailable'


# Context is shared between multiple threads/processes.
# This class simplifies and centralizes read/write of the state:
class GatewayconfigSharedState:

    def __init__(self):
        self.wifi_list_cache = []
        self.should_scan_wifi = False
        self.should_advertise_bluetooth = True
        self.is_advertising_bluetooth = False
        self.are_diagnostics_ok = False
        self.public_key = PUBLIC_KEY_UNAVAILABLE

    def to_s(self):
        return json.dumps(vars(self))

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
