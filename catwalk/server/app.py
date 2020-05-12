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
The app module of catwalk, defines and instantiates the main flask app.
Contains decorated flask functions, see help on each function for details.
"""
import json
import yaml
import logging
import copy
import os.path as osp
from uuid import uuid4

from flask import Flask, Response, request
from werkzeug.exceptions import BadRequest
from schema import SchemaError

from ..utils import get_model_class
from ..helpers.configuration import app_config
from ..helpers.logging import get_logger_from_app_config

from ..validation.schema import get_request_schema
from ..validation.model import is_loaded_model, ModelIOTypes

# Init Flask app
app = Flask(__name__)
model = None
in_schema = None

# Default to Flask's logger
logger = app.logger
logger.setLevel(logging.INFO)


def json_response(response_data, status_code=200) -> Response:
    """A helper function that returns a JSON response with the correct headers.

    :param dict response_data: The data to output as a JSON response.
    :param int status_code: The HTTP status code.
    :return Response: the HTTP response object.
    """
    if status_code != 200:
        logger.error("Returning code {} with message {}".format(status_code, response_data["output"]["message"]))

    json_str = json.dumps(response_data)
    return Response(json_str, status_code, mimetype="application/json")


def api_error(message, status_code=500, request_data=None) -> Response:
    """A helper function that returns a JSON response for a server error.

    :param str message: The error message to return.
    :param int status_code: The HTTP status code.
    :param dict request_data: Optional request data that was sent (this may be empty for e.g. a 400 Bad Request).
    :return Response: the HTTP response object.
    """
    if request_data is not None:
        response = copy.deepcopy(request_data)
    else:
        response = {}
    response["output"] = {"message": message}
    return json_response(response, status_code)


def ensure_correlation_id(data):
    """Checks for a "correlation_id" key and generates one if it doesn't exist.

    :param dict data:
    """
    if "correlation_id" not in data:
        data["correlation_id"] = str(uuid4())


def ensure_model(data):
    """Makes sure thet a "model" key is in the data dict.

    :param dict data:
    """
    if model is not None and "model" not in data:
        data["model"] = {
            "name": model.info["name"],
            "version": model.info["version"]
        }


@app.route("/info")
def info() -> Response:
    """The info end-point, returns metadata about the loaded model.
    :return Response:
    """
    logger.info("Info message received")
    if model is None:
        return api_error("No model loaded.")

    return json_response(model.info)


@app.route("/predict", methods=["POST"])
def predict() -> Response:
    """The predict end-point, validates and runs the predict method on the loaded model.

    :return Response:
    """
    logger.info("Predict message received")

    # Early exit if no model is loaded
    if model is None:
        return api_error("No model loaded.")

    try:
        # Try to parse the JSON body
        data = request.get_json()
        # Try to validate the input data
        in_schema.validate(data)
    except BadRequest:
        return api_error("Invalid POST data: JSON parse error.", 400)
    except SchemaError as err:
        return api_error("Invalid POST data: " + err.code, 400)

    ensure_correlation_id(data)
    ensure_model(data)

    # Test to see if the model loaded matches the request
    if not is_loaded_model(data, model.info):
        return api_error("Model not found.", 404, data)

    # All checks complete, run predict
    logger.info("correlation_id: %s data validated.", data["correlation_id"])

    X = data["input"]

    # PANDAS_DATA_FRAME mode supports receiving data as a dict OR a list
    did_receive_dict = isinstance(data["input"], dict) or data["input"] is None
    if model.io_type == ModelIOTypes.PANDAS_DATA_FRAME:
        if did_receive_dict:
            X = [X]
        X = pd.DataFrame.from_dict(X)

    r = model.predict(X)

    if model.io_type == ModelIOTypes.PANDAS_DATA_FRAME:
        r = r.to_dict(orient="records")

        # PANDAS_DATA_FRAME mode supports receiving data as a dict OR a list
        # `to_dict(orient="records")` will always return a list, so if we received a dict, we want to convert the output
        if did_receive_dict:
            # return the last result if we received a dict
            r = r[-1]

    # Save the result to the request object and return
    data["output"] = r

    logger.info("correlation_id: %s returning response.", data["correlation_id"])

    return json_response(data)


@app.route("/status")
def status():
    """A simple status end-point for health checks on the service
    """
    return ""


def load_model(path):
    """Loads a model from the given path.

    :param str path:
    :return (Model, dict): The loaded model and its metadata
    """
    # Make sure the path is absolute
    path = osp.abspath(path)

    # Import and construct the model
    Model = get_model_class(path)
    if Model is None:
        return

    m = Model(path)

    # Load the metadata file
    with open(osp.join(path, "model.yml"), "r") as fp:
        info = yaml.safe_load(fp)
    m.info = info
    m.io_type = ModelIOTypes.get_io_type(m.info)

    app_config.set_nested("model.name", info["name"])
    app_config.set_nested("model.version", info["version"])

    # pandas must be installed by a model's requirements.txt, to avoid binary incompatabilities between versions
    # this will succeed if the model has the requirement (this is test in the test_model script)
    if m.io_type == ModelIOTypes.PANDAS_DATA_FRAME:
        global pd
        try:
            import pandas
            pd = pandas
        except ImportError:
            logger.error("Unable to import pandas. Was it in your requirements.txt?")

    return m


def init(config_path, model_path):
    global logger, model, in_schema

    app_config.load(config_path)

    logger = get_logger_from_app_config(__name__)
    if config_path is not None and osp.exists(config_path):
        logger.info("Loaded config: {}".format(config_path))

    model = load_model(model_path)

    if model is None:
        logger.error("Unable to load model: %s", model_path)
    else:
        in_schema = get_request_schema(model.info["schema"]["input"], model.io_type)
        logger.info("Initialised model: %s:%s", model.info["name"], model.info["version"])

    return app
