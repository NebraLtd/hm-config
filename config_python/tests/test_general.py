# We have some files which just contain variable declarations
# which drag down the test coverage % artificially, we need to
# include them in the test scope so they are considered for
# coverage calculation, hence we include them here.

# Test Cases
from config_python import uuids  # noqa:F401
from config_python import add_gateway_pb2  # noqa:F401
from config_python import assert_location_pb2  # noqa:F401
from config_python import diagnostics_pb2  # noqa:F401
from config_python import wifi_connect_pb2  # noqa:F401
from config_python import wifi_remove_pb2  # noqa:F401
from config_python import wifi_services_pb2  # noqa:F401
from config_python import variant_definitions  # noqa:F401
