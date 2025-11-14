"""Unit tests for genoplot.constants module."""

import pytest

from genoplot.constants import (
    BASE_FONT_WIDTH,
    DEFAULT_FONT_SIZE,
    DEFAULT_HMARGIN,
    DEFAULT_INDIVIDUAL_COLOR,
    DEFAULT_PAGE_MARGIN,
    DEFAULT_SYMBOL_SIZE,
    DUPLICATE_CONNECTOR_COLOR,
    FONT_HEIGHT_MULTIPLIER,
    MAX_OVERLAP_ITERATIONS,
    OVERLAP_ADJUSTMENT_STEP,
    TEXT_WIDTH_ADJUSTMENT,
    TEXT_WIDTH_THRESHOLD,
    Direction,
    Sex,
)


class TestSexEnum:
    """Tests for Sex enum."""

    def test_male_value(self):
        """Test that Male has correct value."""
        assert Sex.MALE.value == "M"

    def test_female_value(self):
        """Test that Female has correct value."""
        assert Sex.FEMALE.value == "F"

    def test_unknown_value(self):
        """Test that Unknown has correct value."""
        assert Sex.UNKNOWN.value == "U"

    def test_enum_members(self):
        """Test that all expected members exist."""
        assert len(Sex) == 3
        assert Sex.MALE in Sex
        assert Sex.FEMALE in Sex
        assert Sex.UNKNOWN in Sex


class TestDirectionEnum:
    """Tests for Direction enum."""

    def test_left_value(self):
        """Test that LEFT has correct value."""
        assert Direction.LEFT.value == "left"

    def test_right_value(self):
        """Test that RIGHT has correct value."""
        assert Direction.RIGHT.value == "right"

    def test_enum_members(self):
        """Test that all expected members exist."""
        assert len(Direction) == 2
        assert Direction.LEFT in Direction
        assert Direction.RIGHT in Direction


class TestDefaultValues:
    """Tests for default constant values."""

    def test_defaults_are_positive(self):
        """Test that numeric defaults are positive."""
        assert DEFAULT_FONT_SIZE > 0
        assert DEFAULT_SYMBOL_SIZE > 0
        assert DEFAULT_HMARGIN >= 0
        assert DEFAULT_PAGE_MARGIN >= 0

    def test_defaults_are_integers(self):
        """Test that defaults are integers where expected."""
        assert isinstance(DEFAULT_FONT_SIZE, int)
        assert isinstance(DEFAULT_SYMBOL_SIZE, int)
        assert isinstance(DEFAULT_HMARGIN, int)
        assert isinstance(DEFAULT_PAGE_MARGIN, int)

    def test_font_constants(self):
        """Test font-related constants."""
        assert BASE_FONT_WIDTH > 0
        assert FONT_HEIGHT_MULTIPLIER > 0
        assert isinstance(BASE_FONT_WIDTH, float)

    def test_text_constants(self):
        """Test text width constants."""
        assert TEXT_WIDTH_THRESHOLD >= 0
        assert TEXT_WIDTH_ADJUSTMENT >= 0

    def test_layout_constants(self):
        """Test layout-related constants."""
        assert MAX_OVERLAP_ITERATIONS > 0
        assert OVERLAP_ADJUSTMENT_STEP > 0

    def test_color_constants(self):
        """Test color constants are valid hex colors."""
        assert DEFAULT_INDIVIDUAL_COLOR.startswith("#")
        assert len(DEFAULT_INDIVIDUAL_COLOR) == 7  # #RRGGBB
        assert DUPLICATE_CONNECTOR_COLOR.startswith("#")
        assert len(DUPLICATE_CONNECTOR_COLOR) == 7


class TestConstantTypes:
    """Tests for constant types and values."""

    def test_constant_immutability(self):
        """Test that enum values cannot be changed."""
        with pytest.raises(AttributeError):
            Sex.MALE.value = "X"

    def test_direction_enum_comparison(self):
        """Test that Direction enum values can be compared."""
        assert Direction.LEFT == Direction.LEFT
        assert Direction.LEFT != Direction.RIGHT

    def test_sex_enum_comparison(self):
        """Test that Sex enum values can be compared."""
        assert Sex.MALE == Sex.MALE
        assert Sex.MALE != Sex.FEMALE
        assert Sex.MALE != Sex.UNKNOWN
