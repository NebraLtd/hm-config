import os
import logging

LOGLEVEL = os.environ.get("LOGLEVEL", "DEBUG")
_log_format = ("%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s "
               "-- %(pathname)s:(%(lineno)d) - %(message)s")


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(LOGLEVEL)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOGLEVEL)
    logger.addHandler(get_stream_handler())
    return logger


def log(class_name):
    return get_logger(class_name)
