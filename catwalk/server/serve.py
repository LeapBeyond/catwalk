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
"""Serve model in either debug mode or production mode"""
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
