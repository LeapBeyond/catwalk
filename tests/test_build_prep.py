import os.path as osp
import re
import shutil
import tempfile
import unittest

from catwalk.cicd import build_prep


class TestBuildPrep(unittest.TestCase):
    def setUp(self) -> None:
        # create a temporary model directory
        self.model_path = tempfile.mkdtemp()
        with open(osp.join(self.model_path, "model.yml"), "w") as fp:
            fp.write("name: TestModel\nversion: 1.0.0")

    def tearDown(self) -> None:
        # cleanup
        shutil.rmtree(self.model_path)

    def test_build_prep(self) -> None:
        kwargs = {
            "model_path": self.model_path,
            "server_config": None,
            "server_port": 9090
        }

        build_prep(**kwargs)

        # check files were created correctly
        created_files = [
            "Dockerfile",
            ".dockerignore"
        ]

        for f in created_files:
            p = osp.join(self.model_path, f)
            self.assertTrue(osp.exists(p), "build_prep failed to create {}".format(f))

            # check vars were replaced
            with open(p) as fp:
                content = fp.read()
                m = re.search(r"{{\s * ([A - Za - z_()'\"])+\s*}}", content)
                if m is None:
                    msg = ""
                else:
                    msg = "Variable {} not replaced in {}".format(m.group(0), p)
                self.assertIsNone(m, msg)


if __name__ == '__main__':
    unittest.main()
