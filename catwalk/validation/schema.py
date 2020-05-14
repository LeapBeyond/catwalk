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
Defines schema format, see individual section for details.
Also contains modules to convert and read data dict to schema format.
"""
import copy

from schema import Schema, And, Or, Optional

from .model import ModelIOTypes

# The SCHEMAS dictionary holds the various schemas by key.
# Schemas can be retrieved from this dict by get_schema (see below).
SCHEMAS = {}

# The property schema defines basic types, str, bool, int, float, as well as flexible array and object types
SCHEMAS["property"] = Or({
    "type": Or("string", "boolean"),
    Optional("nullable"): bool
}, {
    "type": "integer",
    Optional("format"): Or("int32", "int64"),
    Optional("nullable"): bool
}, {
    "type": "number",
    Optional("format"): Or("float32", "float64"),
    Optional("nullable"): bool
}, {
    "type": "array",
    "items": dict,
    Optional("nullable"): bool
}, {
    "type": "object",
    "properties": dict,
    Optional("nullable"): bool
})

# The object schema defines the format for objects
SCHEMAS["object"] = {
    "type": "object",
    "properties": {
        str: SCHEMAS["property"]
    }
}

# The IO schema is used in the model's specs and can be either an array or object
SCHEMAS["io"] = Or(SCHEMAS["object"], {
    "type": "array",
    "items": SCHEMAS["object"]
})

# The meta schema is the schema used for the model.yml file
SCHEMAS["meta"] = Schema({
    "name": And(str, len),
    "version": And(str, len),
    "contact": {
        "name": And(str, len),
        "email": And(str, len)
    },
    Optional("io_type"): Or(ModelIOTypes.PYTHON_DICT, ModelIOTypes.PANDAS_DATA_FRAME),
    "schema": {
        "input": SCHEMAS["io"],
        "output": SCHEMAS["io"]
    }
})

# The info_response schema is the format of a response to the info request.
# Right now it's the same as the meta schema.
SCHEMAS["info_response"] = SCHEMAS["meta"]

# The request shell defines a schema for general requests.
# The "input" key is None, and is filled in via the get_request_schema function below.
SCHEMAS["request_shell"] = {
    "correlation_id": And(str, len),
    "model": {
        "name": And(str, len),
        "version": And(str, len)
    },
    Optional("extra_data"): dict,
    "input": None
}

# The response shell defines a schema for general responses.
# The "response" key is None, and is filled in via the get_response_schema function below.
SCHEMAS["response_shell"] = copy.deepcopy(SCHEMAS["request_shell"])
SCHEMAS["response_shell"]["output"] = None

# Make the correlation_id optional in the request
SCHEMAS["request_shell"][Optional("correlation_id")] = SCHEMAS["request_shell"]["correlation_id"]
del SCHEMAS["request_shell"]["correlation_id"]

# Make the model optional in the request
SCHEMAS["request_shell"][Optional("model")] = SCHEMAS["request_shell"]["model"]
del SCHEMAS["request_shell"]["model"]


def get_schema(name) -> Schema:
    """Retrieves a schema from the SCHEMAS dict.

    :param str name: The name of the Schema to retrieve
    :return Schema: The matching Schema or None
    """
    if name in SCHEMAS:
        return SCHEMAS[name]


def to_schema(data) -> Schema:
    """Recursively converts data from a swagger dictionary format into a Schema object.

    :param dict data: The swagger schema.
    :return Schema:
    """
    schema = None
    if data["type"] == "string":
        schema = str
    elif data["type"] == "boolean":
        schema = bool
    elif data["type"] == "integer":
        schema = int
    elif data["type"] == "number":
        schema = Or(float, int)
    elif data["type"] == "array":
        schema = [to_schema(data["items"])]
    elif data["type"] == "object":
        schema = {}
        for key, value in data["properties"].items():
            schema[key] = to_schema(value)
    if "nullable" in data and data["nullable"]:
        schema = Or(None, schema)
    return Schema(schema)


def get_request_schema(input_schema, io_type=ModelIOTypes.PYTHON_DICT) -> Schema:
    """Retrieves a request Schema object by copying the request_shell Schema and filling in the "input" key.

    :param Schema|dict input_schema: The input schema to put in the "input" key. Can be a dict or Schema object.
    :param str io_type: The IO type of the model @see ModelIOTypes.
    :return Schema: the complete request Schema object
    """
    if isinstance(input_schema, dict):
        or_wrap_array = io_type == ModelIOTypes.PANDAS_DATA_FRAME and input_schema["type"] == "object"
        input_schema = to_schema(input_schema)
        if or_wrap_array:
            input_schema = Or([input_schema], input_schema)
    request_shell = copy.deepcopy(SCHEMAS["request_shell"])
    request_shell["input"] = input_schema
    return Schema(request_shell)


def get_response_schema(input_schema, output_schema, io_type=ModelIOTypes.PYTHON_DICT, include_correlation_id=True) -> Schema:
    """Retrieves a response Schema object by copying the response_shell Schema and filling in the "input" and
    "output" keys.

    :param Schema|dict input_schema: The input schema to put in the "input" key. Can be a dict or Schema object.
    :param Schema|dict output_schema: The output schema to put in the "output" key. Can be a dict or Schema
                                            object.
    :param str io_type: The IO type of the model @see ModelIOTypes.
    :param bool include_correlation_id: Some responses do not require the correlation_id.
                                            Set this to false to remove it from the Schema.
    :return Schema: the complete response Schema object
    """
    if isinstance(input_schema, dict):
        or_wrap_array = io_type == ModelIOTypes.PANDAS_DATA_FRAME and input_schema["type"] == "object"
        input_schema = to_schema(input_schema)
        if or_wrap_array:
            input_schema = Or([input_schema], input_schema)
    if isinstance(output_schema, dict):
        or_wrap_array = io_type == ModelIOTypes.PANDAS_DATA_FRAME and output_schema["type"] == "object"
        output_schema = to_schema(output_schema)
        if or_wrap_array:
            output_schema = Or([output_schema], output_schema)
    response_shell = copy.deepcopy(SCHEMAS["response_shell"])
    if not include_correlation_id:
        del response_shell["correlation_id"]
    response_shell["input"] = input_schema
    response_shell["output"] = output_schema
    return Schema(response_shell)
