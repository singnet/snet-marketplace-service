import logging
import sys
FORMATTER = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
import os

def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler



def get_level(log_level):
    if log_level == "INFO":
        return logging.INFO
    if log_level == "DEBUG":
        return logging.DEBUG

    return logging.INFO


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    log_level=os.environ.get('LOG_LEVEL',"INFO")
    logger.setLevel(get_level(log_level))
    return logger
