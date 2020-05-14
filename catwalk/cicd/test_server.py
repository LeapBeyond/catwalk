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
Test server with the following steps:
Uses base test python file,
set up model server,
test http responses,
validate model metadata,
validate model I/O,
test with specified correlation_id,
test with a specified model,
test with extra data,
test error 404 response.
"""
import logging
from os import path as osp
import unittest

from schema import SchemaError
import yaml

from ..validation.schema import get_schema, get_response_schema
from ..validation.model import ModelIOTypes
from ..server import app as app_server
from .base_test import BaseTest


class TestServer(BaseTest):
    def __init__(self, model_path, *args, **kwargs):
        super().__init__(model_path, *args, **kwargs)
        self.config_path = None

    def setUp(self):
        super().setUp()

        meta_path = osp.join(self.model_path, "model.yml")
        with open(meta_path, "r") as fp:
            meta = yaml.safe_load(fp)

        self.logger.info("Testing server with model: " + meta["name"])

        app_server.init(self.config_path, self.model_path)
        app_server.app.config["TESTING"] = True

        self.app_logger = app_server.app.logger
        self.original_log_level = self.app_logger.level
        self.app_logger.setLevel(logging.CRITICAL)

        self.client = app_server.app.test_client()

    def runTest(self):
        self._test_status()
        model_info = self._test_info()
        self._test_predict(model_info)

    def tearDown(self):
        self.app_logger.setLevel(self.original_log_level)
        super().tearDown()

    def _test_status(self):
        self.logger.info("Testing HTTP GET /status")

        response = self.client.get("/status")

        self.assertEqual(response.status_code, 200,
                         "Response code to /status should be 200. Got code {}".format(response.status_code))

        self.assertEqual(len(response.data), 0,
                         "Response body to /status should be empty")

    def _test_info(self):
        self.logger.info("Testing HTTP GET /info")

        response = self.client.get("/info")

        self.assertEqual(response.status_code, 200,
                         "Response code to /info should be 200. Got code {}".format(response.status_code))

        self.assertTrue(response.is_json,
                        "Response to /info should be json object")

        info_schema = get_schema("info_response")
        data = response.get_json()

        try:
            info_schema.validate(data)
        except SchemaError as err:
            self.logger.error(err)
            self.fail("Invalid model metadata")

        return data

    def _test_predict(self, model_info):
        self.logger.info("Testing HTTP POST /predict")

        # Load the test data
        X_test, y_test = app_server.model.load_test_data(self.model_path)

        io_type = ModelIOTypes.get_io_type(model_info)

        if io_type == ModelIOTypes.PANDAS_DATA_FRAME:
            X_test = X_test.to_dict(orient="records")
        elif model_info["schema"]["input"]["type"] != "array":
            X_test = X_test[0]

        def test_request(data):
            # Make the request
            response = self.client.post("/predict", json=data)

            self.assertEqual(response.status_code, 200,
                             "Response code to /predict should be 200. Got code {}".format(response.status_code))

            self.assertTrue(response.is_json,
                            "Response to /predict should be json object")

            response_data = response.get_json()

            # Validate against the output schema
            out_schema = get_response_schema(model_info["schema"]["input"], model_info["schema"]["output"], io_type)

            try:
                out_schema.validate(response_data)
            except SchemaError as err:
                self.fail(err)

            return response_data

        request_data = {
            "input": X_test,
        }
        response_data = test_request(request_data)

        self.assertIn("correlation_id", response_data, "correlation_id not returned")

        self.assertIn("model", response_data, "model not returned")

        model_data = {
            "name": model_info["name"],
            "version": model_info["version"]
        }
        self.assertDictEqual(response_data["model"], model_data,
                             "model returned but not a match")

        # Test with specified correlation_id
        request_data["correlation_id"] = "1A"
        response_data = test_request(request_data)
        self.assertEqual(response_data["correlation_id"], "1A", "correlation_id returned did not match")

        # Test with a specified model
        request_data["model"] = model_data
        response_data = test_request(request_data)
        self.assertDictEqual(response_data["model"], model_data,
                             "model returned did not match")

        # Test with extra_data
        request_data["extra_data"] = {
            "foo": "bar"
        }
        response_data = test_request(request_data)
        self.assertIn("extra_data", response_data, "extra_data not returned")
        self.assertDictEqual(request_data["extra_data"], response_data["extra_data"],
                             "extra_data returned but not equal")

        # Test the 400 response

        response = self.client.post("/predict", json="This should fail")

        self.assertEqual(response.status_code, 400,
                         "Response code to /predict with bad data should be 400. Got code {}".format(response.status_code))

        self.assertTrue(response.is_json,
                        "Response to /predict with bad data should be json object")

        response_data = response.get_json()
        self.assertIn("message", response_data["output"],
                      "Response to /predict with bad data should include a message")

        # Test the 404 response

        def test_404():
            response = self.client.post("/predict", json=request_data)

            self.assertEqual(response.status_code, 404,
                             "Response code to /predict with wrong model should be 404. Got code {}".format(
                                 response.status_code))

            self.assertTrue(response.is_json,
                            "Response to /predict with wrong model should be json object")

            response_data = response.get_json()
            self.assertIn("message", response_data["output"],
                          "Response to /predict with wrong model should include a message")

        request_data["model"]["name"] = "This should fail"
        test_404()

        request_data["model"]["name"] = model_info["name"]
        request_data["model"]["version"] = "This should fail"
        test_404()


def test_server(model_path="."):
    suite = unittest.TestSuite()
    suite.addTest(TestServer(model_path))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()
