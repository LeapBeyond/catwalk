from . import app, nginx


def serve(model_path=".", server_config=None, server_port=9090, debug=False):
    if debug:
        # serve the model in debug mode
        app.init(server_config, model_path)
        app.app.run(host="0.0.0.0", port=server_port)
    else:
        # serve the model in production mode
        nginx.start_nginx(server_config, model_path, server_port)

    return 0
