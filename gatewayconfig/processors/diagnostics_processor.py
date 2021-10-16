import json
import requests
from retry import retry

from gatewayconfig.logger import get_logger
from gatewayconfig.gatewayconfig_shared_state import GatewayconfigSharedState

logger = get_logger(__name__)
DIAGNOSTICS_REFRESH_SECONDS = 60


class DiagnosticsProcessor:
    def __init__(self, diagnostics_json_url, shared_state: GatewayconfigSharedState):
        self.shared_state = shared_state
        self.diagnostics_json_url = diagnostics_json_url

    @retry(delay=DIAGNOSTICS_REFRESH_SECONDS)
    def run(self):
        logger.debug("Running DiagnosticsProcessor")
        logger.debug(self.shared_state)
        self.read_diagnostics()

    def read_diagnostics_and_get_ok(self):
        logger.debug("Reading diagnostics from %s" % self.diagnostics_json_url)
        response = requests.get(self.diagnostics_json_url)
        diagnostics_json = response.json()
        logger.debug("Read diagnostics %s" % diagnostics_json)
        are_diagnostics_ok = diagnostics_json['PF']
        return are_diagnostics_ok

    def read_diagnostics(self):
        try:
            self.shared_state.are_diagnostics_ok = self.read_diagnostics_and_get_ok()

        except FileNotFoundError:
            self.shared_state.are_diagnostics_ok = False

        except json.JSONDecodeError:
            self.shared_state.are_diagnostics_ok = False

        except ValueError:
            self.shared_state.are_diagnostics_ok = False

        except Exception as e:
            logger.warn("Unexpected error when trying to read diagnostics file: %s" % e)
