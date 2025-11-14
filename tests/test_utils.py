"""Unit tests for genoplot.utils module."""

import pytest

from genoplot.exceptions import InvalidParameterError
from genoplot.utils import calculate_text_size, strip_name, stripName


class TestCalculateTextSize:
    """Tests for calculate_text_size function."""

    def test_single_string(self):
        """Test with a single string."""
        width, height = calculate_text_size("Hello", 12)
        assert width > 0
        assert height > 0
        assert isinstance(width, float)
        assert isinstance(height, float)

    def test_list_of_strings(self):
        """Test with a list of strings."""
        width, height = calculate_text_size(["Line 1", "Line 2"], 10)
        assert width > 0
        assert height > 0
        # Height should be approximately double for two lines
        single_width, single_height = calculate_text_size("Line 1", 10)
        assert height > single_height

    def test_empty_string(self):
        """Test with empty string."""
        width, height = calculate_text_size("", 10)
        assert width == 0
        assert height > 0  # Height depends on font size

    def test_empty_list(self):
        """Test with empty list."""
        width, height = calculate_text_size([], 10)
        assert width == 0
        assert height == 0

    def test_negative_font_size(self):
        """Test that negative font size raises error."""
        with pytest.raises(InvalidParameterError) as exc_info:
            calculate_text_size("test", -10)
        assert "font_size" in str(exc_info.value)
        assert "must be positive" in str(exc_info.value)

    def test_zero_font_size(self):
        """Test that zero font size raises error."""
        with pytest.raises(InvalidParameterError):
            calculate_text_size("test", 0)

    def test_different_font_sizes(self):
        """Test that larger font size produces larger dimensions."""
        width_small, height_small = calculate_text_size("Test", 10)
        width_large, height_large = calculate_text_size("Test", 20)
        assert width_large > width_small
        assert height_large > height_small


class TestStripName:
    """Tests for strip_name function."""

    def test_remove_quotes(self):
        """Test removal of quote characters."""
        assert strip_name("O'Brien") == "OBrien"
        assert strip_name('Name "Nickname"') == "Name Nickname"

    def test_remove_punctuation(self):
        """Test removal of punctuation."""
        assert strip_name("Smith, John") == "Smith John"
        assert strip_name("Dr. Smith") == "Dr Smith"

    def test_replace_tabs(self):
        """Test that tabs are replaced with spaces."""
        assert strip_name("Name\tWith\tTabs") == "Name With Tabs"

    def test_none_input(self):
        """Test that None input returns None."""
        assert strip_name(None) is None

    def test_empty_string(self):
        """Test that empty string returns empty string."""
        assert strip_name("") == ""

    def test_complex_name(self):
        """Test with complex name containing multiple special characters."""
        result = strip_name("O'Brien, John (Jr.)")
        assert "'" not in result
        assert "," not in result
        assert "(" not in result
        assert ")" not in result
        assert "." not in result

    def test_backward_compatibility_alias(self):
        """Test that stripName alias works the same as strip_name."""
        test_name = "O'Brien, Test"
        assert stripName(test_name) == strip_name(test_name)
