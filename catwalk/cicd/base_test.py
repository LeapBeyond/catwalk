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
"""Setup base test, create logger, and install requirements"""
import logging
import os.path as osp
import sys
import unittest

from ..utils import install_requirements


class BaseTest(unittest.TestCase):
    def __init__(self, model_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_path = osp.abspath(model_path)

    def setUp(self):
        super().setUp()

        # Create a logger
        logging.basicConfig(stream=sys.stderr)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.logger.info("Testing " + self.model_path)

        self._install_requirements()

    def _install_requirements(self):
        status_code = install_requirements(self.model_path)
        self.assertEqual(status_code, 0, "Pip install -r requirements.txt failed.")
        self.logger.info("Installed requirements.txt")
