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
from os.path import join

import pickle


class Model(object):
    def __init__(self, path="."):
        """The Model constructor.

        Use this to initialise your model, including loading any weights etc.

        :param str path: The full path to the folder in which the model is located.
        """
        # Unpickle the model artifact
        with open(join(path, "model.pkl"), "rb") as fp:
            model_artifact = pickle.load(fp)

        # Extract the model and test data
        self._model = model_artifact["model"]
        self._X_test = model_artifact["X_test"]
        self._y_test = model_artifact["y_test"]

    def load_test_data(self, path=".") -> (list, list):
        """Loads and returns test data.

        Format of the returned data is similar to pd.DataFrame.records, a list of key-value pairs.

        :param str path: The full path to the folder in which the model is located.
        :return: Tuple of feature, target lists.
        """
        # The test data needs to be json-serializable, so here we're using `ndarray.tolist()
        # to convert to a plain python list
        return [{"X": self._X_test.tolist()}], [{"y": self._y_test.tolist()}]

    def predict(self, X) -> dict:
        """Uses the model to predict a value.

        :param dict X: The features to predict against
        :return: The prediction result
        """
        y = self._model.predict(X["X"])
        # Again we're using `ndarray.tolist() to convert the model output to a plain python list
        return {"y": y.tolist()}
