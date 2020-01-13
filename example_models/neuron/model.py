import numpy as np


class Model(object):
    """This Model implements an ANN neuron with a sigmoid activation function.
    """

    def __init__(self, path="."):
        """The Model constructor.

        Use this to initialise your model, including loading any weights.

        :param str path: The full path to the folder in which the model is located.
        """
        pass

    def load_test_data(self, path="./") -> (list, list):
        """Loads and returns test data.

        Format of the returned data is similar to pd.DataFrame.records, a list of key-value pairs.

        :param str path: The full path to the folder in which the model is located.
        :return: Tuple of feature, target lists.
        """
        features = [{
            "inputs": [0.5],
            "weights": [1.0]
        }, {
            "inputs": [0.5, 0.5],
            "weights": [1.0, 0.5]
        }]

        targets = [{
            "activation": 0.6224593312018546
        }, {
            "activation": 0.679178699175393
        }]

        return features, targets

    def predict(self, X) -> dict:
        """Uses the model to predict a value.

        In this example, the inputs and weights are used to activate a sigmoid function.

        :param dict X: The features to predict against
        :return: The prediction result
        """
        # calculate input as dot product between inputs and weights
        x = np.dot(X["inputs"], X["weights"])

        # The sigmoid
        y = 1.0 / (1 + np.exp(-x))

        return {
            "activation": y
        }


if __name__ == "__main__":
    m = Model()

    X_test, y_test = m.load_test_data()
    for idx, X in enumerate(X_test):
        print(X)
        y = m.predict(X)
        print(y)
