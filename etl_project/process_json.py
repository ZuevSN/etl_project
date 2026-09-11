# etl_project.process_json.py

import json

def get_dict(path):
    with open(path, 'r', encoding='utf-8') as f:
        dict_json = json.load(f)
        return dict_json