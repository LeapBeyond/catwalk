from . import app, nginx
from ..utils import install_requirements


def serve(model_path=".", server_config=None, server_port=9090, debug=False):
    status_code = install_requirements(model_path)
    if status_code != 0:
        return status_code

    if debug:
        # serve the model in debug mode
        app.init(server_config, model_path)
        app.app.run(host="0.0.0.0", port=server_port)
    else:
        # serve the model in production mode
        nginx.start_nginx(server_config, model_path, server_port)

    return 0
