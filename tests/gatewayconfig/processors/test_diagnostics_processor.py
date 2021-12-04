from unittest import TestCase
from unittest.mock import patch

from gatewayconfig.gatewayconfig_shared_state import GatewayconfigSharedState
from gatewayconfig.processors.diagnostics_processor import DiagnosticsProcessor


class TestDiagnosticsProcessor(TestCase):

    # This method will be used by the mock to replace requests.get
    def mocked_requests_get(*args, **kwargs):
        DIAGNOSTICS_JSON_MOCK = {
            "AN": "acrobatic-neon-caribou", "APPNAME": "Indoor", "BA": "dev-marvin", "BCH": 976046, "BN": "snowy-river",
            "BSP": 98.337, "BT": True, "BUTTON": 26, "CELLULAR": False, "E0": "00:BD:27:78:06:EF", "ECC": True,
            "ECCOB": True, "FR": "915", "FRIENDLY": "Nebra Indoor Hotspot Gen 1", "FW": "2021.08.16.1",
            "ID": "851af059f032f4708fc6b77d07e9bc15", "LOR": False, "LTE": False, "MAC": "eth0", "MC": "yes",
            "MD": "yes", "MH": "959816", "MN": "symmetric", "MR": True, "MS": False,
            "OK": "11cdcEkzjvbGRwpNkihsqoM4yCsrw66jCznJkVuJDcyTf5xKJP", "PF": True,
            "PK": "11cecEkzjvbGdwpNkihsqoM4yCsrw66jCznJkVuJDcyTf5xKJP", "RE": "US915", "RESET": 38,
            "RPI": "0000000057a920e3", "SPIBUS": "spidev1.2", "STATUS": 25, "TYPE": "Full", "VA": "NEBHNT-IN1",
            "W0": "C8:FE:30:FF:F1:72", "last_updated": "21:38 UTC 21 Aug 2021"
            }

        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        return MockResponse(DIAGNOSTICS_JSON_MOCK, 200)

    @patch("requests.get", side_effect=mocked_requests_get)
    def test_read_diagnostics(self, diagnostics_json_mock):
        shared_state = GatewayconfigSharedState()
        self.assertEqual(shared_state.are_diagnostics_ok, False)
        diagnostics_processor = DiagnosticsProcessor('url/ignored', shared_state)

        diagnostics_processor.read_diagnostics()
        # sleep(1)
        self.assertEqual(shared_state.are_diagnostics_ok, True)
