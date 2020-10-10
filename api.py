import json
from collections import OrderedDict
from typing import List, Dict

import requests
import yaml

from config import FAKE_API

BASEURL = "https://plugins.matomo.org/api/2.0/"


def load_additional_data():
    with open("data.yaml") as f:
        return yaml.safe_load(f)


def fetch_plugins(version="3.30.0", themes=False) -> List[Dict]:
    if FAKE_API:
        with open(version + ".json") as f:
            return json.load(f)["plugins"]
    r = requests.get(BASEURL + ("themes" if themes else "plugins") + "?piwik=" + version)
    return r.json()["plugins"]


def preprocess_plugin_data(plugin):
    requires = plugin["versions"][-1]["requires"]
    if "matomo" in requires:
        plugin["supports_version"] = requires["matomo"]
    else:
        plugin["supports_version"] = requires["piwik"]
    del plugin["versions"]
    return plugin


def get_all_plugins():
    plugins = OrderedDict()
    matomo4_plugins = fetch_plugins("4.0.0")
    matomo4_plugins += fetch_plugins("4.0.0", themes=True)
    supported_plugins = 0
    unsupported_plugins = 0
    for plugin in matomo4_plugins:
        plugin["supports4"] = True
        supported_plugins += 1
        plugin = preprocess_plugin_data(plugin)
        plugins[plugin["name"]] = plugin

    matomo3_plugins = fetch_plugins()
    matomo3_plugins += fetch_plugins(themes=True)

    for plugin in matomo3_plugins:
        plugin["supports4"] = False
        plugin = preprocess_plugin_data(plugin)

        name = plugin["name"]
        if name not in plugins:
            unsupported_plugins += 1
            plugins[name] = plugin

    def function(plugin):
        downloads = plugin[1]["numDownloads"]
        if not downloads:
            return 0
        return -downloads

    for name in ["CustomDimensions"]:
        # CustomDimensions became a core plugin
        del plugins[name]
        unsupported_plugins -= 1

    data = load_additional_data()
    plugins_new = {}
    for name, plugin in plugins.items():
        if name in data:
            plugin = {**plugin, **data[name]}
        plugins_new[name] = plugin
    plugins = plugins_new
    plugins = OrderedDict(
        sorted(plugins.items(),
               key=function))
    return plugins, supported_plugins, unsupported_plugins
