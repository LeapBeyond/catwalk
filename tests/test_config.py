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
"""Module to check configurations"""
import unittest
import tempfile
import os

from catwalk.helpers.configuration import app_config


class TestConfig(unittest.TestCase):

    def test_config(self):
        print("Testing empty config")

        app_config.clear()
        self.assertIsNone(app_config.get("test.config.path"), "Empty config was not empty")

        # create app config file
        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, "w") as tmp:
                tmp.write("""
                property: true
                nested:
                    item: "foo"
                """)

            app_config.load(path)

            self.assertTrue(app_config.get("property"), "Config property not found")

            value = app_config.get_nested("nested.item")
            self.assertEqual(value, "foo", "Nested config item not found.")
        finally:
            os.remove(path)

        app_config.set_nested("nested.item2", "bar")
        value = app_config.get_nested("nested.item2")
        self.assertEqual(value, "bar", "Nested config item not found.")


if __name__ == '__main__':
    unittest.main()
