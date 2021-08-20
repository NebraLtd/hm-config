import json

# Context is shared between multiple threads/processes.
# This class simplifies and centralizes read/write of the state:
class GatewayconfigSharedState:

    def __init__(self):
        self.wifi_list_cache = []
        self.should_scan_wifi = False
        self.should_advertise_bluetooth = True
        self.is_advertising_bluetooth = False
        self.are_diagnostics_ok = False

    def to_s(self):
        return json.dumps(vars(self))