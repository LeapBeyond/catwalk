import logging
import os.path as osp
import subprocess
import sys
import unittest


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
        requirements_path = osp.join(self.model_path, "requirements.txt")
        if osp.exists(requirements_path):
            status_code = subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                                                cwd=self.model_path)
            self.assertEqual(status_code, 0, "Pip install failed.")
            self.logger.info("Installed requirements.txt")
