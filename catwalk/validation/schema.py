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
# The "request" key is None, and is filled in via the get_request_schema function below.
SCHEMAS["request_shell"] = {
    "correlation_id": And(str, len),
    "model": {
        "name": And(str, len),
        "version": And(str, len)
    },
    Optional("extra_data"): dict,
    "request": None
}

# The response shell defines a schema for general responses.
# The "response" key is None, and is filled in via the get_response_schema function below.
SCHEMAS["response_shell"] = copy.deepcopy(SCHEMAS["request_shell"])
SCHEMAS["response_shell"]["response"] = None

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


def get_request_schema(request_schema, io_type=ModelIOTypes.PYTHON_DICT) -> Schema:
    """Retrieves a request Schema object by copying the request_shell Schema and filling in the "request" key.

    :param Schema|dict request_schema: The request schema to put in the "request" key. Can be a dict or Schema object.
    :param str io_type: The IO type of the model @see ModelIOTypes.
    :return Schema: the complete request Schema object
    """
    if isinstance(request_schema, dict):
        or_wrap_array = io_type == ModelIOTypes.PANDAS_DATA_FRAME and request_schema["type"] == "object"
        request_schema = to_schema(request_schema)
        if or_wrap_array:
            request_schema = Or([request_schema], request_schema)
    request_shell = copy.deepcopy(SCHEMAS["request_shell"])
    request_shell["request"] = request_schema
    return Schema(request_shell)


def get_response_schema(request_schema, response_schema, io_type=ModelIOTypes.PYTHON_DICT, include_correlation_id=True) -> Schema:
    """Retrieves a response Schema object by copying the response_shell Schema and filling in the "request" and
    "response" keys.

    :param Schema|dict request_schema: The request schema to put in the "request" key. Can be a dict or Schema object.
    :param Schema|dict response_schema: The response schema to put in the "response" key. Can be a dict or Schema
                                            object.
    :param str io_type: The IO type of the model @see ModelIOTypes.
    :param bool include_correlation_id: Some responses do not require the correlation_id.
                                            Set this to false to remove it from the Schema.
    :return Schema: the complete response Schema object
    """
    if isinstance(request_schema, dict):
        or_wrap_array = io_type == ModelIOTypes.PANDAS_DATA_FRAME and request_schema["type"] == "object"
        request_schema = to_schema(request_schema)
        if or_wrap_array:
            request_schema = Or([request_schema], request_schema)
    if isinstance(response_schema, dict):
        or_wrap_array = io_type == ModelIOTypes.PANDAS_DATA_FRAME and response_schema["type"] == "object"
        response_schema = to_schema(response_schema)
        if or_wrap_array:
            response_schema = Or([response_schema], response_schema)
    response_shell = copy.deepcopy(SCHEMAS["response_shell"])
    if not include_correlation_id:
        del response_shell["correlation_id"]
    response_shell["request"] = request_schema
    response_shell["response"] = response_schema
    return Schema(response_shell)
