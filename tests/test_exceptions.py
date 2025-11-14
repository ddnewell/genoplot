"""Unit tests for genoplot.exceptions module."""

import pytest

from genoplot.exceptions import (
    FamilyNotFoundError,
    GedcomParseError,
    GenoplotError,
    IndividualNotFoundError,
    InvalidLayoutError,
    InvalidParameterError,
    PedigreeNotDefinedError,
)


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""

    def test_base_exception(self):
        """Test that GenoplotError is the base exception."""
        assert issubclass(GedcomParseError, GenoplotError)
        assert issubclass(IndividualNotFoundError, GenoplotError)
        assert issubclass(FamilyNotFoundError, GenoplotError)
        assert issubclass(InvalidLayoutError, GenoplotError)
        assert issubclass(InvalidParameterError, GenoplotError)
        assert issubclass(PedigreeNotDefinedError, GenoplotError)

    def test_all_inherit_from_exception(self):
        """Test that all custom exceptions inherit from Exception."""
        assert issubclass(GenoplotError, Exception)


class TestIndividualNotFoundError:
    """Tests for IndividualNotFoundError."""

    def test_message_includes_id(self):
        """Test that error message includes individual ID."""
        err = IndividualNotFoundError(123)
        assert "123" in str(err)
        assert "Individual" in str(err)

    def test_stores_individual_id(self):
        """Test that individual_id attribute is stored."""
        err = IndividualNotFoundError(456)
        assert err.individual_id == 456


class TestFamilyNotFoundError:
    """Tests for FamilyNotFoundError."""

    def test_message_includes_id(self):
        """Test that error message includes family ID."""
        err = FamilyNotFoundError(789)
        assert "789" in str(err)
        assert "Family" in str(err)

    def test_stores_family_id(self):
        """Test that family_id attribute is stored."""
        err = FamilyNotFoundError(101)
        assert err.family_id == 101


class TestInvalidParameterError:
    """Tests for InvalidParameterError."""

    def test_message_includes_param_info(self):
        """Test that error message includes parameter information."""
        err = InvalidParameterError("font_size", -10, "must be positive")
        message = str(err)
        assert "font_size" in message
        assert "-10" in message
        assert "must be positive" in message

    def test_stores_parameter_details(self):
        """Test that parameter details are stored."""
        err = InvalidParameterError("width", 0, "must be greater than zero")
        assert err.param_name == "width"
        assert err.param_value == 0

    def test_message_without_reason(self):
        """Test that error message works without optional reason."""
        err = InvalidParameterError("height", -5)
        message = str(err)
        assert "height" in message
        assert "-5" in message


class TestOtherExceptions:
    """Tests for other exception classes."""

    def test_gedcom_parse_error(self):
        """Test GedcomParseError can be raised."""
        with pytest.raises(GedcomParseError):
            raise GedcomParseError("Invalid GEDCOM format")

    def test_invalid_layout_error(self):
        """Test InvalidLayoutError can be raised."""
        with pytest.raises(InvalidLayoutError):
            raise InvalidLayoutError("Layout calculation failed")

    def test_pedigree_not_defined_error(self):
        """Test PedigreeNotDefinedError can be raised."""
        with pytest.raises(PedigreeNotDefinedError):
            raise PedigreeNotDefinedError("Pedigree reference is None")
