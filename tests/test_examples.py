import os
import os.path as osp
import time
import unittest

from catwalk.cicd import test_model, test_server, build_prep, build, test_image


class TestExamples(unittest.TestCase):

    def setUp(self):
        self.run_docker_tests = os.environ.get("GITHUB_WORKFLOW", None) is None
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
        print(model_path)
        r = test_model(model_path)
        self.assertTrue(r)
        r = test_server(model_path)
        self.assertTrue(r)

        # if the docker client works, we can run the docker image tests
        if self.run_docker_tests:
            server_port = 9090 + (self.i % 2)
            build_prep(model_path=model_path, server_port=server_port)
            build(model_path, no_cache=True, push=False)
            time.sleep(1)
            r = test_image(model_path=model_path, server_port=server_port)
            self.assertTrue(r)
            time.sleep(1)
            self.i += 1


if __name__ == '__main__':
    unittest.main()
