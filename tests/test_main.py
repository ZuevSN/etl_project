# tests/test_main.py
import pytest
from etl_project.main import is_even, safe_float


@pytest.mark.parametrize(
    "num, expected, error_text",
    [
        (6, True, "Проверка четности"),
        (11, False, "Проверка нечетности"),
    ],
)
def test_is_even(num, expected, error_text):
    assert is_even(num) == expected, error_text

@pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param(1, 1, id="int_positive"),
        pytest.param(-1, -1, id="int_negative"),
        pytest.param(0, 0, id="int_zero"),
        pytest.param(2.1, 2.1, id="float_positive"),
        pytest.param('abc', 0, id="string_letters"),
        pytest.param('1.5', 0, id="string_number"),
        pytest.param(True, 0, id="boolean_true"),
        pytest.param(False, 0, id="boolean_false"),
        pytest.param(None, 0, id="none"),
        pytest.param({}, 0, id="empty_dict"),
        pytest.param([], 0, id="empty_list"),
        pytest.param(float("inf"), float("inf"), id="infinity"),
        pytest.param(float("-inf"), float("-inf"), id="negative_infinity")
    ],
)

def test_to_float(value, expected):
    assert safe_float(value) == expected
