##############################################################################
#
# Original Copyright 2019 Amazon.com Inc
# Original: https://github.com/awslabs/amazon-sagemaker-examples/tree/master/advanced_functionality/scikit_bring_your_own/container/decision_trees
# Modifications to this file Copyright 2019 Leap Beyond Emerging Technologies Ltd.
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
""" This file follows the Amazon SageMaker example here:
https://github.com/awslabs/amazon-sagemaker-examples/tree/master/advanced_functionality/scikit_bring_your_own/container/decision_trees

There are two notable differences:
1) model_server_workers has a max value.
2) nginx conf is written at runtime so that we can support variable port numbers.
3) supports SSL
4) able to run as a non-root user
5) supports a dynamic port
"""
import multiprocessing
import os
import os.path as osp
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
import logging

from jinja2 import Environment, PackageLoader

from ..helpers.configuration import app_config
from ..helpers.logging import get_logger_from_app_config

# Setup some worker variables
cpu_count = multiprocessing.cpu_count()
model_server_timeout = os.environ.get("MODEL_SERVER_TIMEOUT", 60)
model_server_workers = int(os.environ.get("MODEL_SERVER_WORKERS", cpu_count))
# Set a limit on the number of workers. 3 makes sense as a default: 1 for REST, 1 for Kafka, and 1 free worker
model_server_workers = min(int(os.environ.get("MAX_MODEL_SERVER_WORKERS", 3)), model_server_workers)


def sigterm_handler(nginx_pid, gunicorn_pid):
    try:
        os.kill(nginx_pid, signal.SIGQUIT)
    except OSError:
        pass
    try:
        os.kill(gunicorn_pid, signal.SIGTERM)
    except OSError:
        pass

    sys.exit(0)


def start_nginx(config=None, model_path=".", port=9090):
    model_path = osp.abspath(model_path)

    app_config_path = config
    if isinstance(app_config_path, str) and app_config_path.lower() == "false":
        app_config_path = None
    app_config.load(app_config_path)

    logger = get_logger_from_app_config(__name__)

    logger.info("Starting nginx/gunicorn with {} workers.".format(model_server_workers))

    ssl_enabled = app_config.get_nested("server.ssl.enabled", False)
    if ssl_enabled:
        cert_path = app_config.get_nested("server.ssl.cert", "/certs/cert.pem")
        cert_path = osp.abspath(cert_path)

        key_path = app_config.get_nested("server.ssl.key", "/certs/key.pem")
        key_path = osp.abspath(key_path)

    # Create a temp dir where the app will sit
    nginx_path = tempfile.mkdtemp()

    env = Environment(loader=PackageLoader("catwalk", "templates"))

    # render the config files
    kwargs = {
        "config": app_config_path if app_config_path else "",
        "model_path": model_path,
        "port": port
    }
    if ssl_enabled:
        kwargs.update({"ssl_cert_path": cert_path, "ssl_key_path": key_path})

    access_log = osp.join(nginx_path, "access.log")
    error_log = osp.join(nginx_path, "error.log")
    kwargs.update({"access_log": access_log, "error_log": error_log})

    nginx_conf = "nginx{}.conf".format("-https" if ssl_enabled else "")
    template = env.get_template(nginx_conf + ".j2")
    rendered = template.render(**kwargs)
    file_path = osp.join(nginx_path, nginx_conf)
    with open(file_path, "w") as fp:
        fp.write(rendered)

    wsgi = "wsgi.py"
    template = env.get_template(wsgi + ".j2")
    rendered = template.render(**kwargs)
    file_path = osp.join(nginx_path, wsgi)
    with open(file_path, "w") as fp:
        fp.write(rendered)

    # link the log streams to stdout/err so they will be logged to the container logs
    Path(access_log).touch()
    Path(error_log).touch()
    if logger.level <= logging.DEBUG:
        subprocess.call(["ln", "-sf", "/dev/stdout", access_log])
    subprocess.call(["ln", "-sf", "/dev/stderr", error_log])

    nginx = subprocess.Popen(["nginx", "-c", osp.join(nginx_path, nginx_conf)])

    gunicorn_args = ["gunicorn"]
    if ssl_enabled:
        gunicorn_args += ["--certfile", cert_path, "--keyfile", key_path]
    gunicorn_args += ["--timeout", str(model_server_timeout),
                      "-k", "gevent",
                      "-b", "unix:/tmp/gunicorn.sock",
                      "-w", str(model_server_workers),
                      "--capture-output",
                      "wsgi:app"]
    gunicorn = subprocess.Popen(gunicorn_args, cwd=nginx_path)

    signal.signal(signal.SIGTERM, lambda a, b: sigterm_handler(nginx.pid, gunicorn.pid))

    # If either subprocess exits, so do we.
    pids = set([nginx.pid, gunicorn.pid])
    while True:
        pid, _ = os.wait()
        if pid in pids:
            break

    sigterm_handler(nginx.pid, gunicorn.pid)
    logger.info("Server exiting")
