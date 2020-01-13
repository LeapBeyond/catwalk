import logging
import sys

from .configuration import app_config


def get_logger_from_app_config(name="__main__"):
    """Creates a logger from the config specified in the yaml file.
    Sets the correct logging level and adds a Kafka Handler if necessary.

    :param str name: the name of the logger.
    :return: Logger
    """
    logger = logging.getLogger(name)

    level = app_config.get_nested("logging.level", "INFO")
    logger.setLevel(level)

    add_default_formatter(logger)

    return logger


def add_default_formatter(logger, fmt="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"):
    """Adds a default Formatter to a Logger object

    :param Logger logger: the Logger instance to add the StreamHandler to.
    :param str fmt: the format of the loffer messages (see logging.Formatter).
    """

    if len(logger.handlers) == 0:
        default_handler = logging.StreamHandler(sys.stderr)
        logger.addHandler(default_handler)
    else:
        default_handler = logger.handlers[0]

    if fmt is not None:
        default_handler.setFormatter(
            logging.Formatter(fmt)
        )
