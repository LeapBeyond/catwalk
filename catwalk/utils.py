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
"""A collection of utilities needed to manage configuration and execution of models."""
import re
import os
import os.path as osp
import importlib.util as il_util
import subprocess
import sys

import yaml


def get_docker_tag(model_meta) -> str:
    """Sanitise a model name in the yaml for safe use as a Docker tag.

    :param dict model_meta:
    :return str: The docker-tag safe string.
    """
    tag = model_meta["name"].lower().strip().replace(" ", "-")
    return re.sub(r"[^A-Za-z0-9\-_]", "", tag)


def get_model_class(model_path=".", model_file_name="model.py", model_class_name="Model", model_module_name="model"):
    """Imports a model from a specified path, and returns the model class implementation from that module.

    :param str model_path: The path to the model directory.
    :param str model_file_name: The filename where the Model class resides.
    :param str model_class_name: The Model class name within the module.
    :param str model_module_name: The Model module name that will be created. TODO: derive this from the model name?
    :return class: The Model class from the module
    """
    model_path = osp.abspath(model_path)
    if not osp.isdir(model_path):
        return

    model_file = osp.join(model_path, model_file_name)
    if not osp.isfile(model_file):
        return

    # dynamically create a python module
    spec = il_util.spec_from_file_location(model_module_name, model_file)
    model_module = il_util.module_from_spec(spec)
    spec.loader.exec_module(model_module)
    sys.modules[model_module_name] = model_module

    if hasattr(model_module, model_class_name):
        return getattr(model_module, model_class_name)


def get_model_tag_and_version(model_path) -> (str, str):
    # Load the model's metadata
    meta_path = osp.join(model_path, "model.yml")
    with open(meta_path, "r") as fp:
        meta = yaml.safe_load(fp)
    model_tag = get_docker_tag(meta)
    model_version = meta["version"]
    return model_tag, model_version


def install_requirements(model_path):
    requirements_path = osp.join(model_path, "requirements.txt")
    if osp.exists(requirements_path):
        cmd = [sys.executable, "-m", "pip", "install"]
        if not os.access(sys.executable, os.W_OK):
            cmd.append("--user")
        cmd += ["-r", "requirements.txt"]
        return subprocess.check_call(cmd, cwd=model_path)
    return 0
