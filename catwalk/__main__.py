import click

from catwalk.cicd import test_model, test_server, build_prep, build, test_image, deploy_prep
from catwalk.server import serve


@click.group()
@click.version_option(message="%(prog)s %(version)s")
def main():
    pass


def model_options(f):
    f = click.option("--model-path", "-m", default=".", envvar="MODEL_PATH",
                     help="The path to the model directory we're working with")(f)
    return f


def server_options(f):
    f = click.option("--server-config", "-c", default=None, envvar="SERVER_CONFIG",
                     help="Specifies the path to the server's configuration.")(f)
    f = click.option("--server-port", "-p", default=9090, envvar="SERVER_PORT",
                     help="Specifies the port Flask will listen on.")(f)
    return f


def docker_options(f):
    f = click.option("--docker-registry", "-r", default="localhost:5000", envvar="DOCKER_REGISTRY",
                     help="Specifies the Docker repo this image is tagged against.")(f)
    return f


@main.command(name="serve")
@model_options
@server_options
@click.option("--debug", "-d", is_flag=True,
              help="Specifies weather or not to run in debug mode (i.e. with debug server etc.).")
@click.option("--test", "-t", is_flag=True, envvar="RUN_TESTS",
              help="Specifies weather or not to run the model tests before starting up the server.")
def cli_serve(**kwargs):
    if kwargs["test"]:
        for test in [test_model, test_server]:
            result = test(kwargs["model_path"])
            if not result:
                return 1
    del kwargs["test"]
    serve(**kwargs)


@main.command(name="test-model")
@model_options
def cli_test_model(**kwargs):
    return 0 if test_model(**kwargs) else 1


@main.command(name="test-server")
@model_options
def cli_test_server(**kwargs):
    return 0 if test_server(**kwargs) else 1


@main.command(name="build-prep")
@model_options
@server_options
@docker_options
def cli_build_prep(**kwargs):
    build_prep(**kwargs)


@main.command(name="build")
@model_options
@docker_options
@click.option("--no-cache", "-C", is_flag=True,
              help="If specified, docker will not use the build cache.")
def cli_build(**kwargs):
    return build(**kwargs)


@main.command(name="test-image")
@model_options
@server_options
@docker_options
@click.option("--server-host", "-s", default="localhost",
              help="Specifies the hostname of the server to test against.")
@click.option("--fail-if-port-in-use", "-f", is_flag=True,
              help="If specified, the test will fail is the specified port is already in use. "
                   "Default behaviour is to kill all containers using the port.")
def cli_test_image(**kwargs):
    return 0 if test_image(**kwargs) else 1


@main.command(name="deploy-prep")
@model_options
@server_options
@docker_options
@click.option("--deploy-mode", "-d", default="compose", type=click.Choice(["compose"]),
              help="The deploy mode controls where we are deploying to. For now, the only option is `compose`.")
@click.option("--volumes", "-v", multiple=True,
              help="Adds extra volume mounts to the deployed container.")
def cli_deploy_prep(**kwargs):
    kwargs["volumes"] = list(kwargs["volumes"])
    deploy_prep(**kwargs)


if __name__ == "__main__":
    main()
