# etl_project.process_json.py

import json


def get_dict(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            dict_json = json.load(f)
            
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e
    if not isinstance(dict_json,dict):
        raise ValueError(f"Expected dict in {path}")
    return dict_json