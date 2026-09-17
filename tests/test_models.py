# tests/test_models.py

import pytest
from unittest.mock import MagicMock
from etl_project.models import ETLContext


@pytest.fixture
def mock_engine():
    return MagicMock()


class TestETLContext:

    def test_mandatory_fields_with_defaults(self, mock_engine):
        ctx = ETLContext(
            engine=mock_engine,
            csv_path="path/data.csv",
            dtype_dict={"Age": "int64"},
            age=30,
        )

        assert ctx.engine is mock_engine
        assert ctx.csv_path == "path/data.csv"
        assert ctx.dtype_dict == {"Age": "int64"}
        assert ctx.age == 30

        assert ctx.multiplier == 0.2
        assert ctx.additional_path is None

    def test_all_fields(self, mock_engine):
        ctx = ETLContext(
            engine=mock_engine,
            csv_path="path/data.csv",
            dtype_dict={"Passenger_id": "int64"},
            age=15,
            multiplier=0.5,
            additional_path="additional_path/new.csv",
        )

        assert ctx.engine is mock_engine
        assert ctx.csv_path == "path/data.csv"
        assert ctx.dtype_dict == {"Passenger_id": "int64"}
        assert ctx.age == 15
        assert ctx.multiplier == 0.5
        assert ctx.additional_path == "additional_path/new.csv"
