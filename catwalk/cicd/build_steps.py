import os.path as osp
import subprocess

from jinja2 import Environment, PackageLoader
import yaml

from ..utils import get_docker_tag
from .. import __version__ as catwalk_version


def get_model_tag_and_version(model_path) -> (str, str):
    # Load the model's metadata
    meta_path = osp.join(model_path, "model.yml")
    with open(meta_path, "r") as fp:
        meta = yaml.safe_load(fp)
    model_tag = get_docker_tag(meta)
    model_version = meta["version"]
    return model_tag, model_version


def build_prep(args):
    """Prepares the model to be Dockerised by generating a dockerimage"""
    args.model_path = osp.abspath(args.model_path)
    model_tag, model_version = get_model_tag_and_version(args.model_path)

    kwargs = vars(args)
    kwargs["catwalk_version"] = catwalk_version
    kwargs["model_tag"] = model_tag
    kwargs["model_version"] = model_version
    if kwargs.get("config", None) is None:
        kwargs["config"] = "/config/application.yml"

    files_to_create = ["Dockerfile", ".dockerignore"]
    env = Environment(loader=PackageLoader("catwalk", "templates"))

    for f in files_to_create:
        template_file = f+".j2"
        if template_file[0] == ".":
            template_file = template_file[1:]
        template = env.get_template(template_file)
        rendered = template.render(**kwargs)
        out_path = osp.join(args.model_path, f)
        with open(out_path, "w") as fp:
            fp.write(rendered)
        print("Wrote " + f)

    return 0


def build(args):
    """Builds the model into a Dockerised model server image.

    :param Namespace args: The cli args.
    """
    args.model_path = osp.abspath(args.model_path)
    model_tag, model_version = get_model_tag_and_version(args.model_path)

    model_path = osp.abspath(args.model_path)

    # Setup
    image_name = "/".join([args.docker_registry, args.docker_namespace, model_tag])

    # Perform the docker build
    cmd = ["docker", "build", model_path]
    cmd += ["-t", image_name+":"+model_version]
    if args.no_cache:
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
