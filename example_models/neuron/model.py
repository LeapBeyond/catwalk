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
"""
Example model:
Artificial neural network
Model to load test data and predict values.
"""
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
