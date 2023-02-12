import json
from collections import OrderedDict
from typing import List, Dict

import requests
import yaml

from config import FAKE_API

BASEURL = "https://plugins.matomo.org/api/2.0/"


def load_additional_data(majorversion: int):
    with open(f"data{majorversion}.yaml") as f:
        return yaml.safe_load(f)


def fetch_plugins(version, themes=False) -> List[Dict]:
    if FAKE_API:
        with open(f"{version}_{themes}.json") as f:
            return json.load(f)["plugins"]
    r = requests.get(BASEURL + ("themes" if themes else "plugins") + "?piwik=" + version)
    with open(f"{version}_{themes}.json", "w") as f:
        json.dump(r.json(),f,indent=2)
    return r.json()["plugins"]


def preprocess_plugin_data(plugin):
    requires = plugin["versions"][-1]["requires"]
    if "matomo" in requires:
        plugin["supports_version"] = requires["matomo"]
    else:
        plugin["supports_version"] = requires["piwik"]
    del plugin["versions"]
    return plugin


def get_all_plugins(majorversion: int):
    plugins = OrderedDict()
    matomo_new_plugins = fetch_plugins(f"{majorversion}.0.0")
    matomo_new_plugins += fetch_plugins(f"{majorversion}.0.0", themes=True)
    supported_plugins = 0
    unsupported_plugins = 0
    for plugin in matomo_new_plugins:
        plugin["supports_new"] = True
        supported_plugins += 1
        plugin = preprocess_plugin_data(plugin)
        plugins[plugin["name"]] = plugin

    print(len(matomo_new_plugins))
    matomo_previous_plugins = fetch_plugins(f"{majorversion - 1}.30.0")
    matomo_previous_plugins += fetch_plugins(f"{majorversion - 1}.30.0", themes=True)
    print(len(matomo_previous_plugins))

    for plugin in matomo_previous_plugins:
        plugin["supports_new"] = False
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

    # if majorversion == 4:
        # for name in {"CustomDimensions"}:
        #     CustomDimensions became a core plugin
            # del plugins[name]
            # unsupported_plugins -= 1

    data = load_additional_data(majorversion)
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
