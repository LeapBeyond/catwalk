import sys
import os.path as osp
import unittest

from schema import SchemaError
import yaml

from ..validation.schema import to_schema, get_schema
from ..validation.model import ModelIOTypes
from .base_test import BaseTest


class TestModel(BaseTest):

    def runTest(self):
        self._test_dir_structure()
        self.meta = self._test_metadata()
        self._test_requirements()
        self.model = self._test_model_interface()

    def _test_dir_structure(self):
        self.logger.info("Test directory structure")

        # Test directory exists
        self.assertTrue(osp.exists(self.model_path), "Model directory does not exist: " + self.model_path)

        # Test expected files exist
        expected_files = ["model.py", "model.yml"]
        for expected_file in expected_files:
            fp = osp.join(self.model_path, expected_file)
            self.assertTrue(osp.exists(fp), "File does not exist: " + expected_file)

    def _test_metadata(self):
        self.logger.info("Test model metadata")

        # Load YAML file
        meta_path = osp.join(self.model_path, "model.yml")
        with open(meta_path, "r") as fp:
            meta = yaml.safe_load(fp)
        self.assertIsInstance(meta, dict, "Metadata should be a dictionary")

        # Validate schema
        meta_schema = get_schema("meta")

        try:
            meta_schema.validate(meta)
        except SchemaError as err:
            self.fail(err)

        return meta

    def _test_requirements(self):
        self.logger.info("Test model requirements.txt")
        requirements_path = osp.join(self.model_path, "requirements.txt")
        requirements_exists = osp.exists(requirements_path)

        io_type = ModelIOTypes.get_io_type(self.meta)
        requirements_is_required = (io_type == ModelIOTypes.PANDAS_DATA_FRAME)

        if requirements_is_required:
            self.assertTrue(requirements_exists, "A requirements.txt file is necessary for this io_type")

        if not requirements_exists:
            return

        with open(requirements_path, "r") as fp:
            requirements = fp.read()

        self.assertGreater(len(requirements), 0, "The requirements.txt file should not be empty")

        if io_type == ModelIOTypes.PANDAS_DATA_FRAME:
            # pandas must be installed by a model's requirements.txt, to avoid binary or API incompatibilities
            # between versions
            self.assertTrue("pandas" in requirements,
                            "io_type: PANDAS_DATA_FRAME requires pandas to be present in your requirements.txt file.")

    def _test_model_interface(self):
        self.logger.info("Test model interface")

        # Test import (via sys path)
        self.logger.info("Test model import")
        sys.path.append(self.model_path)
        try:
            from model import Model
        except Exception as err:
            self.logger.error("from model import Model failed")
            self.fail(err)

        self.logger.info("Test model construction")
        # Test interface
        m = Model(self.model_path)
        self.assertIsInstance(m, Model)

        self.logger.info("Test loading model test data")
        # Test loading test data
        X_test, y_test = m.load_test_data(self.model_path)

        io_type = ModelIOTypes.get_io_type(self.meta)

        if io_type == ModelIOTypes.PYTHON_DICT:
            _type = list
        elif io_type == ModelIOTypes.PANDAS_DATA_FRAME:
            import pandas as pd
            _type = pd.DataFrame
        else:
            self.fail("Unsupported IO type: " + io_type)

        self.assertIsInstance(X_test, _type)
        self.assertIsInstance(y_test, _type)
        self.assertEqual(len(X_test), len(y_test))

        self.logger.info("Test using the provided test data")

        # Create schemas from validation file
        in_schema = to_schema(self.meta["schema"]["input"])
        out_schema = to_schema(self.meta["schema"]["output"])

        # Validate model I/O
        if io_type == ModelIOTypes.PANDAS_DATA_FRAME or self.meta["schema"]["input"]["type"] == "array":
            self._validate(X_test, y_test, in_schema, out_schema, m, io_type)
        else:
            for idx, X in enumerate(X_test):
                y = y_test[idx]
                self._validate(X, y, in_schema, out_schema, m)

        return m

    def _validate(self, X, y, in_schema, out_schema, model, io_type=ModelIOTypes.PYTHON_DICT):
        # Validate against schemas
        try:
            if io_type == ModelIOTypes.PANDAS_DATA_FRAME:
                in_schema.validate(X.to_dict(orient="records"))
            else:
                in_schema.validate(X)
        except SchemaError as err:
            self.logger.error("Input schema validation failed")
            self.logger.error("Input:", X)
            self.fail(err)

        try:
            if io_type == ModelIOTypes.PANDAS_DATA_FRAME:
                out_schema.validate(y.to_dict(orient="records"))
            else:
                out_schema.validate(y)
        except SchemaError as err:
            self.logger.error("Expected output schema validation failed")
            self.logger.error("Input:", X)
            self.logger.error("Expected:", y)
            self.fail(err)

        # Call predict
        r = model.predict(X)

        try:
            # Validate result against out schemas
            if io_type == ModelIOTypes.PANDAS_DATA_FRAME:
                out_schema.validate(r.to_dict(orient="records"))
            else:
                out_schema.validate(r)
        except SchemaError as err:
            self.logger.error("Result schema validation failed")
            self.logger.error("Input:", X)
            self.logger.error("Expected:", y)
            self.logger.error("Result:", r)
            self.fail(err)

        # Check model gives the expected answer
        try:
            if io_type == ModelIOTypes.PANDAS_DATA_FRAME:
                self.assertEqual(r.to_dict(), y.to_dict())
            else:
                self.assertEqual(r, y)
        except AssertionError as e:
            self.logger.error("Result is not what was expected")
            self.logger.error(r)
            self.logger.error(y)
            raise e


def test_model(model_path="."):
    suite = unittest.TestSuite()
    suite.addTest(TestModel(model_path))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()
