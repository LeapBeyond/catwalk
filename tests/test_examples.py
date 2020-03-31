import unittest
import os
import os.path as osp
import sys

from catwalk.cicd import test_model, test_server


class TestExamples(unittest.TestCase):
    def test_examples(self):
        root = os.getcwd()

        while not osp.exists(osp.join(root, "example_models")):
            if root == "/":
                self.fail("Could not find example_models directory via upward search")

            root, tail = osp.split(root)

        examples_path = osp.join(root, "example_models")
        for root, dirs, files in os.walk(examples_path):
            for dir in dirs:
                print(dir)
                r = test_model(osp.join(root, dir))
                self.assertTrue(r)
                r = test_server(osp.join(root, dir))
                self.assertTrue(r)
            break


if __name__ == '__main__':
    unittest.main()
