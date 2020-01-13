import pandas as pd
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

    def load_test_data(self, path="./") -> (pd.DataFrame, pd.DataFrame):
        """Loads and returns test data.

        Format of the returned data is a Pandas DataFrame.

        :param str path: The full path to the folder in which the model is located.
        :return: Tuple of feature, target DataFrames.
        """
        features = pd.DataFrame.from_dict({
            "inputs": [[0.5], [0.5, 0.5]],
            "weights": [[1.0], [1.0, 0.5]]
        })

        targets = pd.DataFrame.from_dict({
            "activation": [0.6224593312018546, 0.679178699175393]
        })

        return features, targets

    def predict(self, X) -> pd.DataFrame:
        """Uses the model to predict a value.

        In this example, the inputs and weights are used to activate a sigmoid function.

        :param pd.DataFrame X: The features to predict against
        :return pd.DataFrame: The prediction result
        """
        y = X.apply(self._activate, axis=1)
        return y.to_frame("activation")

    def _activate(self, X):
        # calculate input as dot product between inputs and weights
        x = np.dot(X["inputs"], X["weights"])

        # The sigmoid
        y = 1.0 / (1 + np.exp(-x))

        return y


if __name__ == "__main__":
    m = Model()

    X_test, y_test = m.load_test_data()
    y = m.predict(X_test)
    print(y.head())
