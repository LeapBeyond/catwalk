##############################################################################
#
# Copyright 2019 Leap Beyond Emerging Technologies B.V. (unless otherwise stated)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
##############################################################################
"""Creates logger"""
import logging
import sys

from .configuration import app_config


def get_logger_from_app_config(name="__main__"):
    """Creates a logger from the config specified in the yaml file.
    Sets the correct logging level and adds a formatter.

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
    :param str fmt: the format of the logger messages (see logging.Formatter).
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
