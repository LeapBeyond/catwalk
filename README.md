# catwalk

`catwalk` is a model wrapping and serving platform.

## Project overview

`catwalk` provides a simple and automated method to wrap a generic python-based model into a production-
ready, dockerised REST API server.
The project aims to automatically wrap a model via a CI/CD pipeline, or locally with a CLI, in a simple and flexible way
and with a single point of configuration.
This model image can then be integrated and deployed into cloud services.

Note that at the time of writing, CD into a cloud service is out-of-scope for `catwalk`.

### Folder structure

- `catwalk` - Contains the `catwalk` python module itself.
- `example_models` - Contains example models for testing and starting points users can use as a basis for their own model.
- `tests` - Contains the unit test suite for catwalk.
- `tutorials` - Contains code for various catwalk tutorials.

## Setup

This project uses [tox](https://tox.readthedocs.io/) to specify tests and environments.  

To develop the module, setup a venv and install it in "editable" mode.

This can be done with `tox`:

```bash
$ tox --devenv catwalk-venv
```

Or with `pip` in an existing venv:

```bash
(catwalk-venv) $ pip install --editable .
```

### Running the tests

The test suite can be simply run with `tox`:

```bash
$ tox
```

## Base image

Model servers images are based on a `catwalk` base image, built from this repo, tagged `catwalk`.
This image sets up the python environment including pre-installing `catwalk`.

To build and push this image, use the following commands:

```bash
$ export CATWALK_VERSION=<version>
$ export DOCKER_REGISTRY=localhost:5000
$ export DOCKER_TAG=${DOCKER_REGISTRY}/catwalk:${CATWALK_VERSION}
$ docker build . -t ${DOCKER_TAG} && docker push ${DOCKER_TAG}
```

The <version> above should match the `catwalk` version.

## Models

Models should be developed independently in secure dev environments.
Models servers themselves will run in a python v3.7 environment, and it is therefore recommended to use this specific 
version when developing the model.

### Interface

Models have two requirements:
1. A specification in `model.yml`
2. An implementation in `model.py`

Models may also contain an optional `requirements.txt` file to manage pip dependencies.

Note: At this time `catwalk` is restricted to only support dependencies installable via pip.

#### Specification

A `model.yml` file must exist, containing:

```yaml
name: "Model name (str)"
version: "Model version (str)"

contact:
  name: "Contact name (str)"
  email: "Contact email (str)"

schema:
  input: "The input schema of the model in OpenAPI format (object / array)"
  output: "The output schema of the model in OpenAPI format (object / array)"
```

#### Implementation

A `model.py` file must exist, implementing a single class called `Model`, that follows this interface:

```python
class Model(object):
    """The Model knows how to load itself, provides test data and runs with `Model::predict`.
    """

    def __init__(self, path="."):
        """The Model constructor.

        Use this to initialise your model, including loading any weights etc.

        :param str path: The full path to the folder in which the model is located.
        """
        pass

    def load_test_data(self, path=".") -> (list, list):
        """Loads and returns test data.

        Format of the returned data is similar to pd.DataFrame.records, a list of key-value pairs.

        :param str path: The full path to the folder in which the model is located.
        :return: Tuple of feature, target lists.
        """
        pass

    def predict(self, X) -> dict:
        """Uses the model to predict a value.

        :param dict X: The features to predict against
        :return: The prediction result
        """
        pass
```

### Examples

Example models are included in this repo for reference and convenience.
Simply run them with your local python.

```bash
$ cd examples/rng
$ python model.py
```

### Support for pandas DataFrames

The pandas DataFrame is the go-to tool for many a pythonic Data Scientist.
To add support for DataFrames in the `Model.predict()` method, specify `io_type: PANDAS_DATA_FRAME` in the model.yml.
This will ensure that the X argument is a pre-constructed DataFrame.
Note that you must return a DataFrame from the `Model.predict()` method as well!

Important points:
- The model's IO schema can either be in "records" format (`[{column -> value}, … , {column -> value}]`) or simplified to a single record (`{column -> value}`).
- pandas must be installed by a model's requirements.txt, to avoid binary or API incompatibilities between versions.

See `examples/dataframe` for an example.

## Model tests

In a CI/CD pipeline, Models are tested before they are wrapped and deployed.
Note that a model may have it's own set of requirements, which will be installed by `catwalk`.

```bash
$ cd /path/to/your/model 
$ catwalk test-model --model-path .
```

## Running the wrapper server

Note that it's best to make the model tests pass (see above) before doing this.
To run the server, run the following:

```bash
$ catwalk serve --model-path /path/to/your/model --debug
```

The `--debug` flag runs a Flask development server, which you can hit it with some requests using curl.

E.g. for the RNG example:

```bash
$ curl -H "Content-Type: application/json" \
    -d '{"correlation_id": "1A", "input": {"seed": 0, "seed_version": 2, "mu": 0.0, "sigma": 1.0}}' \
    http://localhost:9090/predict
```

You can optionally specify the model to run in the request.
The server will return a 404 if that specific model and version is not loaded.
E.g. for the RNG example:

```bash
$ curl -H "Content-Type: application/json" \
    -d '{"correlation_id": "1A", "model": {"name": "RNGModel", "version": "0.0.1"}, "input": {"seed": 0, "seed_version": 2, "mu": 0.0, "sigma": 1.0}}' \
    http://localhost:9090/predict
```

Models also have `/status` and `/info` end points.
Both are GET requests, and one returns a `200` if the server is healthy, while the other returns the information
contained in `model.yml`. 

### Sending arbitrary extra data

Sometimes in a stateless API chain you would like to send some additional data along with the request.
Whatever's in this key should not be not validated or touched by the server, and be returned in the result. 
You can do this with an `extra_data` key in the JSON.

E.g. for the RNG example:

```bash
$ curl -H "Content-Type: application/json" \
    -d '{"correlation_id": "1A", "extra_data": {"foo": "bar"}, "input": {"seed": 0, "seed_version": 2, "mu": 0.0, "sigma": 1.0}}' \
    http://localhost:9090/predict
```

### How the server is productionised

The server is implemented with Flask, but Flask's own development server is not safe or scalable for production.
Following the examples from [Amazon SageMaker](https://github.com/awslabs/amazon-sagemaker-examples/tree/master/advanced_functionality/scikit_bring_your_own/container/decision_trees)
and [Ansible](https://docs.ansible.com/ansible-container/container_yml/pods.html), we have opted to use nginx and
gunicorn to productionise the model.
This creates a fast, concurrent WSGI server.

If you have a local installation of nginx, you can run the server in production mode:

```bash
$ catwalk serve --model-path /path/to/model
```

Note that this command is the same as the development server, but without the `--debug` flag.

#### Using environment variables in production

The production-ready server can use environment variables to set arguments such as model path, config path and server port.
Setting these will override anything passed as a CLI argument.

```bash
$ export MODEL_PATH=/path/to/env/model
$ export SERVER_CONFIG=/path/to/env/conf/application.yml
$ export SERVER_PORT=<some port number>
$ catwalk serve
```

### Server configuration

The server can load an `application.yml` configuration file, which controls various parameters such as logging level and
SSL. 

#### Enabling HTTPS (SSL) support

The REST API is http by default, to enable https, add the following to the `application.yml` config file:

```yaml
server:
  ssl:
    enabled: true
    cert: /certs/cert.pem
    key: /certs/key.pem
```

Then place your cert.pem (CA cert) and your key.pm (private key) in the config directory.
See `conf/local` for an example.

In a deployment this `certs` folder should be mounted as a shared secret.

## Building the server image

Building the server image is achieved with the build command.
Check the help in the script for all the arguments, including docker registry and port.

For integration in a CD pipeline, the image is built in two steps:

```bash
$ catwalk build-prep --model-path /path/to/your/model
$ catwalk build --model-path /path/to/your/model
```

The first step creates the Dockerfile for the model to be wrapped, whereas the second step performs a docker build and push.

### Testing the built image

One you have a model wrapped in a server image, you can test it locally with the `test-image` command.

```bash
$ catwalk test-image --model-path /path/to/your/model
```

## CI/CD integration

To integrate catwalk into a CI/CD pipeline, configure the following steps:

1. Test model (`catwalk test-model --model-path /path/to/model`)
1. Test server (`catwalk test-server --model-path /path/to/model`)
1. Build prep (`catwalk build-prep --model-path /path/to/model`)
1. Build (`catwalk build --model-path /path/to/model`)
1. (optional) Test image (`catwalk test-image --model-path /path/to/model`)

N.B. In order for the CI/CD pipeline to function correctly, the build machine will need:
- python 3.7 and pip;
- internet access;
- docker build access;
- docker push credentials for the registry.

## License

Copyright 2020 Leap Beyond Analytics

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
