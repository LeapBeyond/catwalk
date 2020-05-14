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
"""Load and read config YAML file"""
import logging
import os.path as osp

from yaml import safe_load

logger = logging.getLogger(__name__)


class ApplicationConfig(dict):
    """The ApplicationConfig class represents a config file.
    """

    def load(self, path):
        """Loads a YAML config file using yaml.safe_load.

        :param str path: The path to the config file.
        :return dict: The loaded config.
        """
        if not path:
            return self

        if not osp.exists(path):
            logger.warning("Config path %s does not exist", path)
            return self

        with open(path, "r") as fp:
            self.update(safe_load(fp))

        return self

    def get_nested(self, key, default=None, delimiter="."):
        """Get a nested value in this config. e.g. {"lvl1": {"lvl2": "foo"}} can be accessed with
            get_nested("lvl1.lvl2").
        """
        split_keys = key.split(delimiter)
        r = self
        for k in split_keys:
            r = r.get(k, default)
            if not isinstance(r, dict):
                break
        return r

    def set_nested(self, key, value, delimiter="."):
        """Set a nested value in this config. e.g. set_nested("lvl1.lvl2", "foo") will set
            {"lvl1": {"lvl2": "foo"}}
        """
        split_keys = key.split(delimiter)
        r = self
        for k in split_keys:
            at_end = k == split_keys[-1]
            v = r.get(k, value if at_end else {})
            r[k] = v
            if isinstance(v, dict):
                r = v


app_config = ApplicationConfig()
