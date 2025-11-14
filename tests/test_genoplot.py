"""Unit tests for genoplot.GenoPlot class."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from genoplot.exceptions import GedcomParseError, InvalidParameterError
from genoplot.genoplot import GenoPlot


class TestGenoPlotInit:
    """Tests for GenoPlot initialization."""

    def test_invalid_font_size(self):
        """Test that negative font size raises error."""
        with pytest.raises(InvalidParameterError) as exc_info:
            with patch("genoplot.genoplot.Pedigree"):
                GenoPlot("test", "/fake/path.ged", font_size=-10)
        assert "font_size" in str(exc_info.value)

    def test_invalid_hmargin(self):
        """Test that negative hmargin raises error."""
        with pytest.raises(InvalidParameterError) as exc_info:
            with patch("genoplot.genoplot.Pedigree"):
                GenoPlot("test", "/fake/path.ged", hmargin=-5)
        assert "hmargin" in str(exc_info.value)

    def test_invalid_symbol_size(self):
        """Test that non-positive symbol_size raises error."""
        with pytest.raises(InvalidParameterError) as exc_info:
            with patch("genoplot.genoplot.Pedigree"):
                GenoPlot("test", "/fake/path.ged", symbol_size=0)
        assert "symbol_size" in str(exc_info.value)

    def test_invalid_page_margin(self):
        """Test that negative page_margin raises error."""
        with pytest.raises(InvalidParameterError) as exc_info:
            with patch("genoplot.genoplot.Pedigree"):
                GenoPlot("test", "/fake/path.ged", page_margin=-10)
        assert "page_margin" in str(exc_info.value)

    def test_nonexistent_gedcom_file(self):
        """Test that nonexistent GEDCOM file raises error."""
        with pytest.raises(GedcomParseError) as exc_info:
            GenoPlot("test", "/nonexistent/file.ged")
        assert "not found" in str(exc_info.value)

    @patch("genoplot.genoplot.Path.exists")
    @patch("genoplot.genoplot.Path.is_file")
    @patch("genoplot.genoplot.Pedigree")
    def test_gedcom_path_is_directory(self, mock_pedigree, mock_is_file, mock_exists):
        """Test that directory path raises error."""
        mock_exists.return_value = True
        mock_is_file.return_value = False

        with pytest.raises(GedcomParseError) as exc_info:
            GenoPlot("test", "/some/directory")
        assert "not a file" in str(exc_info.value)

    @patch("genoplot.genoplot.Path.exists")
    @patch("genoplot.genoplot.Path.is_file")
    @patch("genoplot.genoplot.Pedigree")
    def test_valid_initialization(self, mock_pedigree, mock_is_file, mock_exists):
        """Test successful initialization with valid parameters."""
        mock_exists.return_value = True
        mock_is_file.return_value = True

        gp = GenoPlot("test_plot", "/fake/test.ged")
        assert gp.name == "test_plot"
        assert gp._output_file.suffix == ".svg"

    @patch("genoplot.genoplot.Path.exists")
    @patch("genoplot.genoplot.Path.is_file")
    @patch("genoplot.genoplot.Pedigree")
    def test_output_file_default(self, mock_pedigree, mock_is_file, mock_exists):
        """Test that default output file is {name}.svg."""
        mock_exists.return_value = True
        mock_is_file.return_value = True

        gp = GenoPlot("myplot", "/fake/test.ged")
        assert gp._output_file == Path("myplot.svg")

    @patch("genoplot.genoplot.Path.exists")
    @patch("genoplot.genoplot.Path.is_file")
    @patch("genoplot.genoplot.Pedigree")
    def test_output_file_custom(self, mock_pedigree, mock_is_file, mock_exists):
        """Test custom output file path."""
        mock_exists.return_value = True
        mock_is_file.return_value = True

        gp = GenoPlot("test", "/fake/test.ged", output_file="custom.svg")
        assert gp._output_file == Path("custom.svg")

    @patch("genoplot.genoplot.Path.exists")
    @patch("genoplot.genoplot.Path.is_file")
    @patch("genoplot.genoplot.Pedigree")
    def test_output_file_adds_svg_extension(self, mock_pedigree, mock_is_file, mock_exists):
        """Test that .svg extension is added if missing."""
        mock_exists.return_value = True
        mock_is_file.return_value = True

        gp = GenoPlot("test", "/fake/test.ged", output_file="output.png")
        assert gp._output_file.suffix == ".svg"
        assert gp._output_file.stem == "output"

    @patch("genoplot.genoplot.Path.exists")
    @patch("genoplot.genoplot.Path.is_file")
    @patch("genoplot.genoplot.Pedigree")
    def test_repr(self, mock_pedigree, mock_is_file, mock_exists):
        """Test __repr__ method."""
        mock_exists.return_value = True
        mock_is_file.return_value = True

        gp = GenoPlot("test", "/fake/test.ged", output_file="out.svg")
        repr_str = repr(gp)
        assert "GenoPlot" in repr_str
        assert "test" in repr_str
        assert "out.svg" in repr_str
