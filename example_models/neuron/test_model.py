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
"""Tests loading data and prediction for the Artificial Neural Network model"""
import unittest
from model import Model


class TestModel(unittest.TestCase):
    def test_model(self):
        m = Model()

        print("Test loading of test data")
        X_test, y_test = m.load_test_data()
        self.assertEqual(len(X_test), len(y_test))

        print("Test predict method")
        for idx, X in enumerate(X_test):
            y = m.predict(X)
            self.assertDictEqual(y, y_test[idx])


if __name__ == '__main__':
    unittest.main()
