import os
import json


def get_parameter(path: str, environment: str, name: str):
    filename = os.path.join(path, os.path.basename(path) + "_parameters.json")
    value = None
    with open(filename) as json_file:
        data = json.load(json_file)
        if name in data[environment]:
            value = data[environment][name]
            if value == "":
                value = None
    return(value)

