import logging
import sys
import os

FORMATTER = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")


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
    log_level = os.environ.get('LOG_LEVEL', "INFO")
    logger.setLevel(get_level(log_level))
    return logger


def file_logger(logger_name):
    logger = logging.getLogger(logger_name)
    file_name = os.environ.get('LOG_PATH', "/var/log/app/module.log")
    handler = logging.FileHandler(file_name)
    handler.setFormatter(FORMATTER)
    logger.addHandler(handler)
    return logger
