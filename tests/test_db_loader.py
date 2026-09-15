# tests/test_main.py
import pytest
from etl_project.db_loader import normalize_column
import pandas as pd

"""
def normalize_column(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(r"\s+", "_", regex=True)
    return df
"""

@pytest.mark.parametrize(
    "input_columns, expected",
    [
        pytest.param(["Passenger Id","Survived "," Pclass","Name"],
                     ["passenger_id","survived","pclass","name"],
                     id="spaces_mixed_case"),
        pytest.param(["Passenger  Id","Survived  ","  Pclass","  NAME  "],
                     ["passenger_id","survived","pclass","name"],
                     id="multi_spaces_mixed_case"),
        pytest.param([],
                     [],
                     id="empty_list_column")
    ],
)
def test_normalize_column(input_columns, expected):
    df = pd.DataFrame({col: [1,2,3] for col in input_columns})
    print(df)
    result = normalize_column(df)
    assert list(result.columns) == expected