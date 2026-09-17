# tests/test_main.py
import pytest
from etl_project.main import is_even, get_float_or_default


@pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param(3, False, id="odd_int_positive"),
        pytest.param(4, True, id="even_int_positive"),
        pytest.param(-1, False, id="odd_int_negative"),
        pytest.param(-8, True, id="even_int_negative"),
        pytest.param(10 * 100, True, id="huge_even_int_positive"),
        pytest.param(0, True, id="int_zero"),
        pytest.param(2.1, False, id="float_positive"),
        pytest.param("abc", False, id="string_letters"),
        pytest.param("1.5", False, id="string_number"),
        pytest.param(True, False, id="boolean_true"),
        pytest.param(False, False, id="boolean_false"),
        pytest.param(None, False, id="none"),
        pytest.param({}, False, id="empty_dict"),
        pytest.param([], False, id="empty_list"),
        pytest.param(float("inf"), False, id="infinity"),
        pytest.param(float("-inf"), False, id="negative_infinity"),
        pytest.param(float("nan"), False, id="nan"),  # неопределенное значение типа 0/0
    ],
)
def test_is_even(value, expected):
    assert is_even(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param(1, 1, id="int_positive"),
        pytest.param(-1, -1, id="int_negative"),
        pytest.param(0, 0, id="int_zero"),
        pytest.param(2.1, 2.1, id="float_positive"),
        pytest.param("abc", 0, id="string_letters"),
        pytest.param("1.5", 0, id="string_number"),
        pytest.param(True, 0, id="boolean_true"),
        pytest.param(False, 0, id="boolean_false"),
        pytest.param(None, 0, id="none"),
        pytest.param(float("inf"), float("inf"), id="infinity"),
        pytest.param(float("-inf"), float("-inf"), id="negative_infinity"),
    ],
)
def test_get_float_or_default(value, expected):
    assert get_float_or_default(value) == expected
