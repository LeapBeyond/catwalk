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
Docker step by step building blocks:
generate docker image, prepare model, and build model
"""
import logging
import os.path as osp
import subprocess

from jinja2 import Environment, PackageLoader

from ..utils import get_model_tag_and_version
from .. import __version__ as catwalk_version

logger = logging.getLogger(__name__)


def build_prep(model_path=".", server_config=None, server_port=9090):
    """Prepares the model to be Dockerised by generating a dockerimage"""
    model_path = osp.abspath(model_path)
    model_tag, model_version = get_model_tag_and_version(model_path)

    if server_config is None:
        server_config = "false"

    kwargs = {
        "catwalk_version": catwalk_version,
        "model_tag": model_tag,
        "model_version": model_version,
        "server_config": server_config,
        "server_port": server_port
    }

    files_to_create = ["Dockerfile", ".dockerignore"]
    env = Environment(loader=PackageLoader("catwalk", "templates"))

    for f in files_to_create:
        template_file = f + ".j2"
        if template_file[0] == ".":
            template_file = template_file[1:]
        template = env.get_template(template_file)
        rendered = template.render(**kwargs)
        out_path = osp.join(model_path, f)
        with open(out_path, "w") as fp:
            fp.write(rendered)
        logger.info("Wrote " + f)


def build(model_path=".", docker_registry=None, push=True, no_cache=False):  # pragma: no cover
    """Builds the model into a Dockerised model server image."""
    model_path = osp.abspath(model_path)
    model_tag, model_version = get_model_tag_and_version(model_path)

    model_path = osp.abspath(model_path)

    # Setup
    image_name_parts = [model_tag]
    if docker_registry is not None:
        image_name_parts.insert(0, docker_registry)
    image_name = "/".join(image_name_parts)
    docker_tag = image_name + ":" + model_version

    # Perform the docker build
    cmd = ["docker", "build", model_path]
    cmd += ["-t", docker_tag]
    if no_cache:
        cmd += ["--no-cache"]

    logger.info(" ".join(cmd))
    result = subprocess.run(cmd, check=True)

    if result.returncode != 0:
        return result.returncode

    logger.info("Successfully built " + docker_tag)

    if not push:
        return 0

    # Perform the docker push
    cmd = ["docker", "push", docker_tag]

    logger.info(" ".join(cmd))
    result = subprocess.run(cmd, check=True)

    return result.returncode
