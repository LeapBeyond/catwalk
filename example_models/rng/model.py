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

    def predict(self, X) -> dict:
        """Uses the model to predict a value.

        In this example, the features are used to seed and call a Gaussian RNG.

        :param dict X: The features to predict against
        :return: The prediction result
        """
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
