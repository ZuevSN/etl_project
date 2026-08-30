# etl_project.csv_handler.py
import csv
from itertools import islice
import pandas as pd
from pathlib import Path


def write_file(path, my_list):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=my_list[1].keys())
        writer.writeheader()
        writer.writerows(my_list)


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        return reader


def get_rows(path, count=0, filters=None):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if filters:
            for filter_func, filter_name, filter_val in filters:
                reader = filter_func(reader, filter_name, filter_val)

        if count == 0:
            return list(reader)
        else:
            return list(islice(reader, count))


def get_len(path):
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f) - 1


def read_csv_to_df(path_to_file):
    path = Path(path_to_file)
    if not path.exists():
        raise FileNotFoundError("Файл не найден")
    if path.suffix.lower() != ".csv":
        raise ValueError("Формат отличается от ожидаемого csv")
    return pd.read_csv(path)
