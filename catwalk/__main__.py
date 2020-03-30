import argparse
import sys
import unittest

from catwalk.cicd import TestModel, TestServer, TestImage
from catwalk.cicd import build_prep, build
from catwalk.server import app, nginx


def serve(args):
    if args.debug:
        # serve the model in debug mode
        app.init(args.config, args.model_path)
        app.app.run(host="0.0.0.0", port=args.port)
    else:
        # serve the model in production mode
        nginx.start_nginx(args)

    return 0


def test_model(args):
    suite = unittest.TestSuite()
    suite.addTest(TestModel(args.model_path))
    unittest.TextTestRunner(verbosity=2).run(suite)


def test_server(args):
    suite = unittest.TestSuite()
    suite.addTest(TestServer(args.model_path))
    unittest.TextTestRunner(verbosity=2).run(suite)


def test_image(args):
    suite = unittest.TestSuite()
    suite.addTest(TestImage(args))
    unittest.TextTestRunner(verbosity=2).run(suite)


commands = {
    "serve": serve,
    "test_model": test_model,
    "test_server": test_server,
    "build_prep": build_prep,
    "build": build,
    "test_image": test_image
}


def main() -> int:
    """The main entry point for catwalk.
    :return int: a status code
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("command", default="help", help="The command to run")
    parser.add_argument("--config", "-c", type=str,
                        help="Specifies the path to the application's configuration.")
    parser.add_argument("--debug", "-d", action="store_true",
                        help="Specifies weather or not to run in debug mode (i.e. with debug server etc.).")
    parser.add_argument("--model-path", "-m", default=".", type=str,
                        help="Specifies the path to the model directory we're serving")
    parser.add_argument("--port", "-p", default=9090, type=int,
                        help="Specifies the port Flask will listen to")
    parser.add_argument("--server-host", "-s", default="localhost", type=str,
                        help="Specifies the hostname of the server.")
    parser.add_argument("--docker-registry", "-r", default="localhost:5000", type=str,
                        help="Specifies the Docker repo this image is tagged against.")
    parser.add_argument("--docker-namespace", "-n", default="catwalk/models", type=str,
                        help="Specifies the namespace this image is tagged within.")
    parser.add_argument("--fail-if-port-in-use", "-f", action="store_true",
                        help="If specified, the test will fail is the specified port is already in use. "
                             "Default behaviour is to kill all containers using the port.")
    parser.add_argument("--no-cache", "-C", action="store_true",
                        help="If specified, docker will not use the build cache.")

    args = parser.parse_args()

    command = commands.get(args.command, None)
    if command is not None:
        return command(args)

    print("Command not found: {}".format(args.command), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
