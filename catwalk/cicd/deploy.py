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
"""Prepares docker compose file for deployment"""
import os.path as osp

from jinja2 import Environment, PackageLoader

from ..utils import get_model_tag_and_version


def deploy_prep_compose(model_path=".", server_config=None, server_port=9090, docker_registry=None,
                        volumes=None):
    """Prepares the model to be deployed with Compose by generating a docker-compose file"""
    model_path = osp.abspath(model_path)
    model_tag, model_version = get_model_tag_and_version(model_path)
    docker_tag = model_tag + ":" + model_version
    image_name_parts = [docker_tag]
    if docker_registry is not None:
        image_name_parts.insert(0, docker_registry)
    image_name = "/".join(image_name_parts)

    if volumes is None:
        volumes = []
    else:
        for i, v in enumerate(volumes):
            local, mount = v.split(":")
            volumes[i] = osp.abspath(local) + ":" + mount

    if server_config is None:
        server_config = "false"
    else:
        server_config_path, server_config_file = osp.split(osp.abspath(server_config))
        server_config = "/config/" + server_config_file
        volumes.append(server_config_path + ":/config")

    kwargs = {
        "docker_registry": docker_registry,
        "model_tag": model_tag,
        "model_version": model_version,
        "docker_tag": docker_tag,
        "image": image_name,
        "server_config": server_config,
        "server_port": server_port,
        "has_volumes": len(volumes) > 0,
        "volumes": volumes
    }

    files_to_create = ["docker-compose.yml"]
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
        print("Wrote " + f)


def deploy_prep(deploy_mode="compose", model_path=".", server_config=None, server_port=9090,
                docker_registry=None, volumes=None):
    if deploy_mode == "compose":
        deploy_prep_compose(model_path, server_config, server_port, docker_registry, volumes)
        return 0
    return 1
