from unittest import TestCase

from catwalk.utils import get_docker_tag


class TestUtils(TestCase):
    def test_get_docker_tag(self):
        tag = get_docker_tag({"name": "ghft3&& *T\"*&E T\"&*    "})
        self.assertEqual(tag, "ghft3-te-t")
