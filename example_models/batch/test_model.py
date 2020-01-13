import unittest
from model import Model


class TestModel(unittest.TestCase):
    def test_model(self):
        m = Model()

        print("Test loading of test data")
        X_test, y_test = m.load_test_data()
        self.assertEqual(len(X_test), len(y_test))

        print("Test predict method")
        y = m.predict(X_test)
        self.assertEqual(y, y_test)


if __name__ == '__main__':
    unittest.main()
