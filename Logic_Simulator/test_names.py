"""Test the names module."""
import pytest

from names import Names


@pytest.fixture
def new_names():
    """Returns a new names instance."""
    return Names()


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["nand4", "DEVICES", "QBAR", "17"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after four names have been added."""
    my_name = Names()
    my_name.lookup(name_string_list)
    return my_name


def test_get_name_string_raises_exceptions(used_names):
    """Test if get_name_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.get_name_string(1.4)
    with pytest.raises(TypeError):
        used_names.get_name_string("hello")
    with pytest.raises(ValueError):
        used_names.get_name_string(-1)


@pytest.mark.parametrize("name_id, expected_string", [
    (0, "nand4"),
    (1, "DEVICES"),
    (2, "QBAR"),
    (3, "17"),
])
def test_get_name_string(used_names, new_names, name_id, expected_string):
    """Test if get_name_string returns the expected string."""
    # Name is present
    assert used_names.get_name_string(name_id) == expected_string
    # Name is absent
    assert new_names.get_name_string(name_id) is None
    # ID is present and correct
    assert used_names.query(expected_string) == name_id


@pytest.fixture
def error_list_one():
    """Return a list of example errors."""
    return ["NO_COLON", "NO_STRING", "NO_RIGHTBRACKET"]


@pytest.fixture
def error_list_two():
    """Return a list of example errors."""
    return ["NO_DOT", "ABSENT_DEVICE"]


@pytest.fixture
def used_errors(error_list_one, error_list_two):
    """Return a names instance after five errors have been added"""
    other_name = Names()
    other_name.unique_error_codes(len(error_list_one))
    other_name.unique_error_codes(len(error_list_two))
    return other_name


def test_unique_error_codes_raises_exceptions(used_errors):
    """Test if unique_error_codes raises expected exceptions."""
    with pytest.raises(TypeError):
        used_errors.unique_error_codes(1.4)
    with pytest.raises(TypeError):
        used_errors.unique_error_codes("hello")
    with pytest.raises(ValueError):
        used_errors.unique_error_codes(-1)


def test_unique_error_codes(used_errors):
    """Test if unique_error_codes adds the correct number of
    errors to global list."""
    # Total number of errors added equals five
    assert used_errors.error_code_count == 5
