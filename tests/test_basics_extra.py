import pytest
from assignments.basics import safe_div, slugify, median

# ----------------------------
# Tests for safe_div
# ----------------------------

def test_safe_div_normal():
    assert safe_div(10, 2) == 5
    assert safe_div(-10, 2) == -5
    assert safe_div(10, -2) == -5
    assert safe_div(0, 10) == 0

def test_safe_div_zero_divisor():
    assert safe_div(10, 0) is None
    assert safe_div(0, 0) is None



# ----------------------------
# Tests for slugify
# ----------------------------

def test_slugify_basic():
    assert slugify(" Hello, World! ") == "hello-world"
    assert slugify("A—B") == "ab"

def test_slugify_spaces_and_hyphens():
    assert slugify("ggg &***          &&***    &&*** ") == "ggg---"
    assert slugify("multiple   spaces here") == "multiple-spaces-here"
    assert slugify("  leading and trailing  ") == "leading-and-trailing"

def test_slugify_punctuation():
    assert slugify("Hello!@# World$%^") == "hello-world"
    assert slugify("---Already-hyphens---") == "---already-hyphens---"

def test_slugify_spaces_and_hyphens_and_punctuation():
    assert slugify("Hello   &&**&  ---  &&&&  world! ") == "hello-------world"

# ----------------------------
# Tests for median
# ----------------------------

def test_median_odd_length():
    assert median([1, 3, 2]) == 2
    assert median([10.0, 5.0, 7.5]) == 7.5

def test_median_even_length():
    assert median([1, 2, 3, 4]) == 2.5
    assert median([10, 20, 30, 40, 50, 60]) == 35.0

def test_median_single_element():
    assert median([42]) == 42

def test_median_empty_list():
    with pytest.raises(ValueError):
        median([])

def test_median_unsorted_input():
    assert median([5, 1, 4, 2, 3]) == 3
