import unittest
import logging

from catwalk.helpers.configuration import app_config
from catwalk.helpers.logging import get_logger_from_app_config


class TestKafkaHandler(unittest.TestCase):

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
