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
"""Module to test logger"""
import unittest
import logging

from catwalk.helpers.configuration import app_config
from catwalk.helpers.logging import get_logger_from_app_config


class TestLoggingHandler(unittest.TestCase):

    def setUp(self):
        super().setUp()

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        self.logger = logger

    def test_logger_from_config(self):
        print("Testing empty app_config")

        app_config.clear()

        lggr = get_logger_from_app_config("__test1__")
        self.assertEqual(len(lggr.handlers), 1)


if __name__ == '__main__':
    unittest.main()
