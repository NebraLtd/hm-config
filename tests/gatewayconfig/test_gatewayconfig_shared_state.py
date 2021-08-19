from unittest import TestCase

from gatewayconfig.gatewayconfig_shared_state import GatewayconfigSharedState

class TestGatewayconfigSha(TestCase):

    def test_init(self):
        shared_state = GatewayconfigSharedState()

        self.assertEqual(shared_state.wifi_list_cache, [])
        self.assertEqual(shared_state.should_scan_wifi, False)
        self.assertEqual(shared_state.should_advertise_bluetooth, True)
        self.assertEqual(shared_state.is_advertising_bluetooth, False)
        self.assertEqual(shared_state.are_diagnostics_ok, False)