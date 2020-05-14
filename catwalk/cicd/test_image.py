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
Test the docker image with the following steps:
create a logger,
load model meta,
create docker client,
check for ports,
spins up container,
test new container with example data,
validate results,
test error 400 response,
tear down test container.
"""
import sys
import unittest
import logging
import time
import json
import yaml
from urllib import request
from urllib.error import HTTPError, URLError
from http.client import RemoteDisconnected
from os import path as osp
import ssl
import random

import docker
from schema import SchemaError

from ..helpers.configuration import app_config

from ..validation.schema import get_schema, get_response_schema
from ..validation.model import ModelIOTypes
from ..utils import get_docker_tag, get_model_class


class TestImage(unittest.TestCase):
    def __init__(self, model_path=".", server_config=None, server_port=9090,
                 docker_registry=None, server_host="localhost", fail_if_port_in_use=False,
                 docker_client=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_path = model_path
        self.server_config = server_config
        self.server_port = server_port
        self.docker_registry = docker_registry
        self.server_host = server_host
        self.fail_if_port_in_use = fail_if_port_in_use
        self.client = docker_client

    def setUp(self):
        super().setUp()

        # Create a logger
        logging.basicConfig(stream=sys.stderr)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Load the model metadata
        self.model_path = osp.abspath(self.model_path)
        meta_path = osp.join(self.model_path, "model.yml")
        with open(meta_path, "r") as fp:
            meta = yaml.safe_load(fp)

        model_tag = get_docker_tag(meta)
        self.tag = "{}:{}".format(model_tag, meta["version"])

        app_config.load(self.server_config)
        ssl_enabled = app_config.get_nested("server.ssl.enabled", False)

        self.http = "http"
        self.ssl_context = None
        if ssl_enabled:
            self.http += "s"
            self.ssl_context = ssl.SSLContext()

        self.logger.info("Testing " + self.tag)

        # Create docker client
        client = docker.from_env() if self.client is None else self.client

        # Check for existing container(s) using the specified port
        containers = client.containers.list(filters={"expose": self.server_port})
        if len(containers) > 0:
            if self.fail_if_port_in_use:
                self.fail("Port in use by the following containers: " + str(containers))

            # Kill any that we find
            for c in containers:
                c.kill()

        # Spin up our container
        volumes = []
        if self.server_config is not None:
            volumes.append("{}:/config:ro".format(osp.abspath(self.server_config)))
        if ssl_enabled:
            volumes.append("{}:/certs:ro".format(osp.abspath(osp.join(self.server_config, "certs"))))

        image_name_parts = [self.tag]
        if self.docker_registry is not None:
            image_name_parts.insert(0, self.docker_registry)
        self.container = client.containers.run("/".join(image_name_parts),
                                               ports={str(self.server_port) + "/tcp": self.server_port},
                                               volumes=volumes,
                                               user=random.randrange(10000, 20000),
                                               detach=True)
        self.client = client

        time.sleep(1)

    def tearDown(self):
        # Shutdown the image
        self.container.kill()
        super().tearDown()

    def runTest(self):
        self.logger.info("Testing image starts correctly")

        # Test container was created
        self.assertEqual(self.container.status, "created",
                         "Container status not \"created\"")

        data = self._test_info()
        self._test_predict(data)

    def _test_info(self):
        # Wait for the server to become responsive...
        response = None
        t = 0
        time_limit = 30
        while response is None:
            self.logger.info("Attempting {} request...".format(self.http))
            try:
                response = request.urlopen("{}://{}:{}/info".format(self.http, self.server_host, self.server_port), context=self.ssl_context)
            except (RemoteDisconnected, ConnectionResetError, URLError) as err:
                print(err)
                time.sleep(1)
                t += 1

                if t > time_limit:
                    self.fail("Container not responsive after {} seconds".format(time_limit))

        self.logger.info("Testing {} GET /info".format(self.http))

        self.assertEqual(response.status, 200,
                         "Response code to /info should be 200. Got code {}".format(response.status))

        data = response.read().decode("utf-8")
        self.assertGreater(len(data), 0,
                           "Response to /info should not be empty")
        data = json.loads(data)
        self.assertIsInstance(data, dict,
                              "Response to /info should be json object")

        info_schema = get_schema("info_response")

        try:
            info_schema.validate(data)
        except SchemaError as err:
            self.fail(err)

        return data

    def _test_predict(self, model_info):
        self.logger.info("Testing {} POST /predict".format(self.http))

        # Load the test data
        Model = get_model_class(self.model_path)
        self.assertIsNotNone(Model, "Could not load Model class")

        m = Model(self.model_path)
        X_test, y_test = m.load_test_data(self.model_path)

        io_type = ModelIOTypes.get_io_type(model_info)

        if io_type == ModelIOTypes.PANDAS_DATA_FRAME:
            # Pandas models test all the data in records format
            X_test = X_test.to_dict(orient="records")
        elif model_info["schema"]["input"]["type"] != "array":
            # Batch models test all the data, non-batch models just use the first row
            X_test = X_test[0]

        request_data = {
            "correlation_id": "1A",
            "extra_data": {
                "foo": "bar"
            },
            "input": X_test,
        }

        # Make the request
        req = request.Request("{}://{}:{}/predict".format(self.http, self.server_host, self.server_port))
        req.add_header("Content-Type", "application/json; charset=utf-8")
        post_data = json.dumps(request_data).encode("utf-8")
        req.add_header("Content-Length", len(post_data))
        response = request.urlopen(req, post_data, context=self.ssl_context)

        self.assertEqual(response.status, 200,
                         "Response code to /predict should be 200. Got code {}".format(response.status))

        data = response.read().decode("utf-8")
        self.assertGreater(len(data), 0,
                           "Response to /predict should not be empty")
        data = json.loads(data)
        self.assertIsInstance(data, dict,
                              "Response to /predict should be json object")

        # Validate against the output schema
        out_schema = get_response_schema(model_info["schema"]["input"], model_info["schema"]["output"], io_type)

        try:
            out_schema.validate(data)
        except SchemaError as err:
            self.fail(err)

        # Test the 400 response

        req = request.Request("{}://{}:{}/predict".format(self.http, self.server_host, self.server_port))
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        post_data = "This should fail".encode("utf-8")
        req.add_header("Content-Length", len(post_data))

        try:
            response = request.urlopen(req, post_data, context=self.ssl_context)
        except HTTPError as err:
            got_error = True
            self.assertEqual(err.status, 400,
                             "Response code to /predict with bad data should be 400. Got code {}".format(err.status))

            data = err.read().decode("utf-8")
            self.assertGreater(len(data), 0,
                               "Response to /predict with bad data should not be empty")

            try:
                data = json.loads(data)
                self.assertIsInstance(data, dict,
                                      "Response to /predict should be json object")
            except json.decoder.JSONDecodeError:
                self.fail("Response to /predict should be json")

        self.assertTrue(got_error)


def test_image(**kwargs):
    suite = unittest.TestSuite()
    suite.addTest(TestImage(**kwargs))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()
