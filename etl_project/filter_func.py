#etl_project.filter_func.py

def minValue(reader, name, value ):
    def check(row):
        raw_value = row.get(name, '').strip()
        if raw_value=='' or raw_value is None:
            return True
        try:
            return float(raw_value) > value
        except TypeError:
            return False
    reader = filter(check, reader)
    return reader

def maxValue(reader, name, value ):
    def check(row):
        raw_value = row.get(name, '').strip()
        if raw_value=='' or raw_value is None:
            return True
        try:
            return float(raw_value) < value
        except TypeError:
            return False
    reader = filter(check, reader)
    return reader

def eqValue(reader, name, value ):
    def check(row):
        raw_value = row.get(name, '').strip()
        if raw_value=='' or raw_value is None:
            return True
        try:
            return float(raw_value) == value
        except TypeError:
            return False
    reader = filter(check, reader)
    return reader