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
