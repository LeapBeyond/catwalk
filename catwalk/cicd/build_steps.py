import os.path as osp
import subprocess

from jinja2 import Environment, PackageLoader

from ..utils import get_model_tag_and_version
from .. import __version__ as catwalk_version


def build_prep(model_path=".", server_config=None, server_port=9090, docker_registry="localhost:5000"):
    """Prepares the model to be Dockerised by generating a dockerimage"""
    model_path = osp.abspath(model_path)
    model_tag, model_version = get_model_tag_and_version(model_path)

    if server_config is None:
        server_config = "false"

    kwargs = {
        "docker_registry": docker_registry,
        "catwalk_version": catwalk_version,
        "model_tag": model_tag,
        "model_version": model_version,
        "server_config": server_config,
        "server_port": server_port
    }

    files_to_create = ["Dockerfile", ".dockerignore"]
    env = Environment(loader=PackageLoader("catwalk", "templates"))

    for f in files_to_create:
        template_file = f+".j2"
        if template_file[0] == ".":
            template_file = template_file[1:]
        template = env.get_template(template_file)
        rendered = template.render(**kwargs)
        out_path = osp.join(model_path, f)
        with open(out_path, "w") as fp:
            fp.write(rendered)
        print("Wrote " + f)


def build(model_path=".", docker_registry="localhost:5000", no_cache=False):  # pragma: no cover
    """Builds the model into a Dockerised model server image."""
    model_path = osp.abspath(model_path)
    model_tag, model_version = get_model_tag_and_version(model_path)

    model_path = osp.abspath(model_path)

    # Setup
    image_name = "/".join([docker_registry, model_tag])

    # Perform the docker build
    cmd = ["docker", "build", model_path]
    cmd += ["-t", image_name+":"+model_version]
    if no_cache:
        cmd += ["--no-cache"]

    print(" ".join(cmd))
    result = subprocess.run(cmd, check=True)

    if result.returncode != 0:
        return result.returncode

    cmd = ["docker", "push", image_name+":"+model_version]

    print(" ".join(cmd))
    result = subprocess.run(cmd, check=True)

    # Cleanup
    return result.returncode
