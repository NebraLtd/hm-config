import logging

import os

LOGLEVEL = os.environ.get("LOGLEVEL", "DEBUG")
# create logger
logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)

# create console handler and set level to debug
stream_handler = logging.StreamHandler()
stream_handler.setLevel(LOGLEVEL)

# create formatter
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S")

# add formatter to stream_handler
stream_handler.setFormatter(formatter)

# add stream_handler to logger
logger.addHandler(stream_handler)
