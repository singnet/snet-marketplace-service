import logging


def configure_log(logger, log_path='/var/log/marketplace/app.log'):

    logger.setLevel(logging.INFO)

    # create a file handler
    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)
