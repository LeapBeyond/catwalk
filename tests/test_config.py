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
