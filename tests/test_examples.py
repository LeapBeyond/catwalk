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
"""
Module to test with example models.
Uses the models in the example_models folder (details of the models can be found there),
and if docker client works, docker image tests will run.
"""
import logging
import os
import os.path as osp
from subprocess import CalledProcessError
import time
import unittest

from catwalk.cicd import test_model, test_server, build_prep, build, test_image

logger = logging.getLogger(__name__)


class TestExamples(unittest.TestCase):

    def setUp(self):
        self.i = 0

    def test_examples(self):
        root = os.getcwd()

        while not osp.exists(osp.join(root, "example_models")):
            if root == "/":
                self.fail("Could not find example_models directory via upward search")

            root, tail = osp.split(root)

        examples_path = osp.join(root, "example_models")
        for root, dirs, files in os.walk(examples_path):
            for dir in dirs:
                self._test_model(osp.join(root, dir))
            break

    def _test_model(self, model_path):
        logger.info("Testing example: " + model_path)
        r = test_model(model_path)
        self.assertTrue(r)
        r = test_server(model_path)
        self.assertTrue(r)

        # if the docker client works, we can run the docker image tests
        server_port = 9090 + (self.i % 2)
        build_prep(model_path=model_path, server_port=server_port)

        try:
            build(model_path, no_cache=True, push=False)
        except (FileNotFoundError, CalledProcessError):
            logger.warning("Docker build failed, we're probably trying to run in an environment without docker."
                           " Ignoring...")
            return

        r = test_image(model_path=model_path, server_port=server_port)
        self.assertTrue(r)
        time.sleep(1)
        self.i += 1


if __name__ == '__main__':
    unittest.main()
