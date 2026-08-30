# etl_project.filter_func.py

import pandas as pd


def minValue(reader, name, value):
    def check(row):
        raw_value = row.get(name, "").strip()
        if raw_value == "" or raw_value is None:
            return True
        try:
            return float(raw_value) > value
        except TypeError:
            return False

    reader = filter(check, reader)
    return reader


def maxValue(reader, name, value):
    def check(row):
        raw_value = row.get(name, "").strip()
        if raw_value == "" or raw_value is None:
            return True
        try:
            return float(raw_value) < value
        except TypeError:
            return False

    reader = filter(check, reader)
    return reader


def eqValue(reader, name, value):
    def check(row):
        raw_value = row.get(name, "").strip()
        if raw_value == "" or raw_value is None:
            return True
        try:
            return float(raw_value) == value
        except TypeError:
            return False

    reader = filter(check, reader)
    return reader


def dfMinValue(df, name, value):
    if name not in df.columns:
        raise KeyError(f"Нет колонки '{name}'")
    return df[pd.to_numeric(df[name], errors="coerce") > value]


def dfMaxValue(df, name, value):
    if name not in df.columns:
        raise KeyError(f"Нет колонки '{name}'")
    return df[pd.to_numeric(df[name], errors="coerce") < value]


def dfEqValue(df, name, value):
    if name not in df.columns:
        raise KeyError(f"Нет колонки '{name}'")
    return df[pd.to_numeric(df[name], errors="coerce") == value]
