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
