import json
import requests
import threading

from gatewayconfig.logger import get_logger
from gatewayconfig.gatewayconfig_shared_state import GatewayconfigSharedState

logger = get_logger(__name__)
DIAGNOSTICS_REFRESH_SECONDS_SLOW = 3600
DIAGNOSTICS_REFRESH_SECONDS_FAST = 60
FAST_DIAGNOSTIC_TIMEOUT = 1800


class DiagnosticsProcessor:
    def __init__(self, diagnostics_json_url, shared_state: GatewayconfigSharedState):
        self.shared_state = shared_state
        self.diagnostics_json_url = diagnostics_json_url
        self.fast_diagnostics_timer = None
        self.fast_diagnostics = False

    def get_refresh_interval(self) -> int:
        if self.fast_diagnostics or not self.shared_state.are_diagnostics_ok:
            return DIAGNOSTICS_REFRESH_SECONDS_FAST
        return DIAGNOSTICS_REFRESH_SECONDS_SLOW

    def schedule_stop_fast_diagnostics(self, timer_seconds=FAST_DIAGNOSTIC_TIMEOUT):
        if self.fast_diagnostics_timer:
            logger.debug("cancelling existing stop fast diagnostic timer")
            self.fast_diagnostics_timer.cancel()

        # trigger the timer to stop advertisement
        self.fast_diagnostics_timer = threading.Timer(timer_seconds,
                                                      self.stop_fast_diagnostics)
        self.fast_diagnostics_timer.start()
        logger.debug('scheduled stop fast diagnostics in %s seconds', timer_seconds)

    def stop_fast_diagnostics(self):
        logger.debug("Stopping fast diagnostics refresh.")
        self.fast_diagnostics = False

    def run(self):
        while True:
            # it will be set to true when someone sets trigger fast_diagnostic event
            # if timeout expires it will be to set to false
            event_state = self.shared_state.run_fast_diagnostic_condition_event.wait(
                timeout=self.get_refresh_interval()
                )
            if event_state:
                logger.debug(f"Fast diagnostics refresh triggered. "
                             f"Will run for {DIAGNOSTICS_REFRESH_SECONDS_FAST} seconds")
                self.shared_state.run_fast_diagnostic_condition_event.clear()
                self.fast_diagnostics = True
                self.schedule_stop_fast_diagnostics()

            logger.debug("Running DiagnosticsProcessor")
            self.read_diagnostics()
            logger.debug(self.shared_state)

    def read_diagnostics_and_get_ok(self):
        logger.debug("Reading diagnostics from %s" % self.diagnostics_json_url)
        response = requests.get(self.diagnostics_json_url, timeout=30)
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
