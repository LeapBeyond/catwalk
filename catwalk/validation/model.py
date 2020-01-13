def is_loaded_model(request, model_info):
    """A simple function to validate if the model in the request matches that in the model info.
    Checks model name and version.

    :param dict request: The incoming request.
    :param dict model_info: The loaded model info.
    :return bool: True if the request matches.
    """
    r_model_info = request["model"]
    return r_model_info["name"] == model_info["name"] and r_model_info["version"] == model_info["version"]


class ModelIOTypes(object):
    """Models can have support for various IO types (what they expect is their "X" argument).
     This class lists the supported values.

    """
    PANDAS_DATA_FRAME = "PANDAS_DATA_FRAME"
    PYTHON_DICT = "PYTHON_DICT"

    @staticmethod
    def get_io_type(model_meta) -> str:
        """Returns the io_type specified in the metadata, or returns the default.
        :param dict model_meta: the model's metadata
        :return str: the io_type
        """
        if "io_type" in model_meta and model_meta["io_type"] in ModelIOTypes.__dict__:
            return model_meta["io_type"]
        return ModelIOTypes.PYTHON_DICT
