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
"""Module to test utils"""
from unittest import TestCase

from catwalk.utils import get_docker_tag


class TestUtils(TestCase):
    def test_get_docker_tag(self):
        tag = get_docker_tag({"name": "ghft3&& *T\"*&E T\"&*    "})
        self.assertEqual(tag, "ghft3-te-t")
