import sys
import unittest
import logging
import yaml
from os import path as osp

from schema import SchemaError

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
        self.client = app_server.app.test_client()

    def runTest(self):
        self._test_status()
        model_info = self._test_info()
        self._test_predict(model_info)

    def _test_status(self):
        self.logger.info("Tessting HTTP GET /status")

        response = self.client.get("/status")

        self.assertEqual(response.status_code, 200,
                         "Response code to /status should be 200. Got code {}".format(response.status_code))

        self.assertEquals(len(response.data), 0,
                          "Response bodyto /status should be empty")

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
            out_schema = get_response_schema(model_info["schema"]["input"], model_info["schema"]["output"])

            try:
                out_schema.validate(response_data)
            except SchemaError as err:
                self.fail(err)

            return response_data

        request_data = {
            "correlation_id": "1A",
            "request": X_test,
        }
        response_data = test_request(request_data)
        self.assertIn("model", response_data, "model not returned")

        model_data = {
            "name": model_info["name"],
            "version": model_info["version"]
        }
        self.assertDictEqual(response_data["model"], model_data,
                             "model returned but not a match")

        # Test with a specified model
        request_data["model"] = model_data
        test_request(request_data)

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
        self.assertIn("message", response_data["response"],
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
            self.assertIn("message", response_data["response"],
                          "Response to /predict with wrong model should include a message")

        request_data["model"]["name"] = "This should fail"
        test_404()

        request_data["model"]["name"] = model_info["name"]
        request_data["model"]["version"] = "This should fail"
        test_404()
