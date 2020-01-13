import re


def get_docker_tag(model_meta) -> str:
    """Sanitise a model name in the yaml for safe use as a Docker tag.

    :param dict model_meta:
    :return str: The docker-tag safe string.
    """
    tag = model_meta["name"].lower().strip().replace(" ", "-")
    return re.sub(r"[^A-Za-z0-9\-_]", "", tag)


if __name__ == "__main__":
    tag = get_docker_tag({
        "name": "ghft3&& *T\"*&E T\"&*    "
    })
    print(tag)
