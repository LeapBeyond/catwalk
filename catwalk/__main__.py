import click

from catwalk.cicd import test_model, test_server, build_prep, build, test_image
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
    f = click.option("--server-config", "-c", default=None, envvar="SERVER_OPTIONS",
                     help="Specifies the path to the server's configuration.")(f)
    f = click.option("--server-port", "-p", default=9090, envvar="SERVER+PORT",
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
def cli_serve(**kwargs):
    return serve(**kwargs)


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
    return 0 if build_prep(**kwargs) else 1


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


if __name__ == "__main__":
    main()
