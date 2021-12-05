from unittest import TestCase
from unittest.mock import patch

from gatewayconfig.gatewayconfig_shared_state import GatewayconfigSharedState


class TestGatewayconfigSha(TestCase):

    def test_init(self):
        shared_state = GatewayconfigSharedState()

        self.assertEqual(shared_state.wifi_list_cache, [])
        self.assertEqual(shared_state.should_scan_wifi, False)
        self.assertEqual(shared_state.should_advertise_bluetooth, True)
        self.assertEqual(shared_state.is_advertising_bluetooth, False)
        self.assertEqual(shared_state.are_diagnostics_ok, False)

    def test_to_s(self):
        shared_state = GatewayconfigSharedState()
        self.assertEqual(shared_state.to_s(),
                         '{"wifi_list_cache": [], "should_scan_wifi": false, "should_advertise_bluetooth": true, '
                         '"is_advertising_bluetooth": false, "are_diagnostics_ok": false, "public_key": "Unavailable"}'
                         )

    @patch('gatewayconfig.gatewayconfig_shared_state.get_public_keys_rust', return_value={'key': 'foo'})
    def test_load_public_key(self, _):
        shared_state = GatewayconfigSharedState()
        shared_state.load_public_key()
        self.assertEqual(shared_state.public_key, 'foo')

    @patch('gatewayconfig.gatewayconfig_shared_state.get_public_keys_rust', return_value={'key': 'foo'})
    def test_load_public_key_dont_override(self, _):
        shared_state = GatewayconfigSharedState()
        shared_state.public_key = 'already_set'
        shared_state.load_public_key()
        self.assertEqual(shared_state.public_key, 'already_set')
