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
import random


class Model(object):
    """This Model implements a random Gaussian number generator.
    """

    def __init__(self, path="."):
        """The Model constructor.

        Use this to initialise your model, including loading any weights.

        :param str path: The full path to the folder in which the model is located.
        """
        pass

    def load_test_data(self, path=".") -> (list, list):
        """Loads and returns test data.

        Format of the returned data is similar to pd.DataFrame.records, a list of key-value pairs.

        :param str path: The full path to the folder in which the model is located.
        :return: Tuple of feature, target lists.
        """
        features = [{
            "seed": 0,
            "seed_version": 2,
            "mu": 0.0,
            "sigma": 1.0
        }, {
            "seed": 1,
            "seed_version": 2,
            "mu": 0.0,
            "sigma": 1.0
        }]

        targets = [{
            "score": 0.9417154046806644
        }, {
            "score": 1.2881847531554629
        }]

        return features, targets

    def predict(self, X) -> list:
        """Uses the model to predict a value.

        In this example, the features are used to seed and call a Gaussian RNG.

        :param dict X: The features to predict against
        :return: The prediction result
        """

        return [self._predict(x) for x in X]

    def _predict(self, X) -> dict:
        random.seed(X["seed"], X["seed_version"])

        return {
            "score": random.gauss(X["mu"], X["sigma"])
        }


if __name__ == "__main__":
    m = Model()

    X_test, y_test = m.load_test_data()
    for idx, X in enumerate(X_test):
        print(X)
        y = m.predict(X)
        print(y)
