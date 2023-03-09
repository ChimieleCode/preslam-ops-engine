import json
from typing import Iterable, List
import yaml
import csv
import os, shutil

from pyparsing import Any
from pathlib import Path


def import_from_json(filepath: Path) -> dict:
    """
    Imports a .json file and converts it into a dictionary
    """
    with open(filepath, 'r') as jsonfile:
        return json.loads(jsonfile.read())


def export_to_json(filepath: Path, data: dict) -> None:
    """
    Exports a given dict into a json file
    """
    with open(filepath, 'w') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False, indent=4)


def import_configuration(config_path: Path, object_hook: object = None) -> Any:
    """
    Imports the config file and returns a dictionary if object_hook is not specified

    Args:
        config_path (Path): config.yaml Path
        object_hook (object, optional): Dataclass structure for config information. Defaults to None.

    Returns:
        Any: config dictionary. If object hook is defined, will return an object_hook.__class__ instance
    """
    with open(config_path) as yamlfile:
        config_dct = yaml.safe_load(yamlfile)

    if object_hook is not None:
        return object_hook(
            **config_dct
        )
    return config_dct


def write_to_csv(file_path: Path, data: Iterable, header: Iterable = None):
    """
    Writes data to csv

    Args:
        file_path (Path): file path
        data (Iterable): data as a matrix
        header (Iterable, optional): Header of csv file. Defaults to None.
    """
    with open(file_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if header is not None:
            writer.writerow(header)
        writer.writerows(data)


def clean_directory(dir_path: Path) -> None:
    """
    Wipes the content of a folder

    Args:
        dir_path (Path): path to folder
    """
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))