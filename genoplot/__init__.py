# Copyright (c) 2017 by Welded Anvil Technologies (David D. Newell). All Rights Reserved.
# This software is the confidential and proprietary information of
# Welded Anvil Technologies (David D. Newell) ("Confidential Information").
# You shall not disclose such Confidential Information and shall use it
# only in accordance with the terms of the license agreement you entered
# into with Welded Anvil Technologies (David D. Newell).
# @author david@newell.at

import logging
import time

import coloredlogs

from .constants import Direction, Sex
from .exceptions import (
    FamilyNotFoundError,
    GedcomParseError,
    GenoplotError,
    IndividualNotFoundError,
    InvalidLayoutError,
    InvalidParameterError,
    PedigreeNotDefinedError,
)
from .family import Family
from .genoplot import GenoPlot
from .individual import Individual
from .pedigree import Pedigree
from .utils import calculate_text_size, strip_name

__version__ = "0.1.0"

__all__ = [
    # Main classes
    "GenoPlot",
    "Pedigree",
    "Individual",
    "Family",
    # Enums and constants
    "Sex",
    "Direction",
    # Utility functions
    "calculate_text_size",
    "strip_name",
    # Exceptions
    "GenoplotError",
    "GedcomParseError",
    "IndividualNotFoundError",
    "FamilyNotFoundError",
    "InvalidLayoutError",
    "InvalidParameterError",
    "PedigreeNotDefinedError",
    # Version
    "__version__",
]

__copyright__ = """
    Copyright (c) 2017 by Welded Anvil Technologies (David D. Newell). All Rights Reserved.
    This software is the confidential and proprietary information of
    Welded Anvil Technologies (David D. Newell) ("Confidential Information").
    You shall not disclose such Confidential Information and shall use it
    only in accordance with the terms of the license agreement you entered
    into with Welded Anvil Technologies (David D. Newell).
    @author david@newell.at
"""

__author__ = "David D. Newell <david@newell.at>"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("genoplot")
coloredlogs.install(level="INFO")


def main(gedcom_file: str = "sample.ged", output_file: str = "output.svg"):
    """
    Example main function for creating a pedigree plot from a GEDCOM file.

    Args:
        gedcom_file: Path to the GEDCOM input file.
        output_file: Path to the SVG output file.

    Returns:
        The GenoPlot object.

    Example:
        >>> from genoplot import main
        >>> plot = main("family.ged", "family.svg")
    """
    import sys
    from pathlib import Path

    gedcom_path = Path(gedcom_file)
    if not gedcom_path.exists():
        logger.error(f"GEDCOM file not found: {gedcom_file}")
        logger.info("Usage: python -m genoplot <gedcom_file> [output_file]")
        sys.exit(1)

    pstart = time.time()

    # Create the plot
    p = GenoPlot(
        name=gedcom_path.stem,
        gedcom_file=gedcom_file,
        output_file=output_file
    )

    # Generate the graph and draw it
    p.create_graph()
    p.draw()

    logger.info(f"Total time to build GenoPlot: {time.time() - pstart:.2f}s")
    logger.info(f"Output written to: {output_file}")

    return p
