#etl_project.filter_func.py

def minValue(reader, name, value ):
    def check(row):
        str = row.get(name, '').strip()
        if str=='' or str is None:
            return True
        try:
            return float(str) > value
        except:
            return False
    reader = filter(check, reader)
    return reader

def maxValue(reader, name, value ):
    def check(row):
        str = row.get(name, '').strip()
        if str=='' or str is None:
            return True
        try:
            return float(str) < value
        except:
            return False
    reader = filter(check, reader)
    return reader

def eqValue(reader, name, value ):
    def check(row):
        str = row.get(name, '').strip()
        if str=='' or str is None:
            return True
        try:
            return float(str) == value
        except:
            return False
    reader = filter(check, reader)
    return reader