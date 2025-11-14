# Copyright (c) 2016 by Welded Anvil Technologies (David D. Newell). All Rights Reserved.
# This software is the confidential and proprietary information of
# Welded Anvil Technologies (David D. Newell) ("Confidential Information").
# You shall not disclose such Confidential Information and shall use it
# only in accordance with the terms of the license agreement you entered
# into with Welded Anvil Technologies (David D. Newell).
# @author david@newell.at

"""Constants and enumerations for the genoplot package."""

from enum import Enum


class Sex(Enum):
    """Biological sex enumeration."""
    MALE = "M"
    FEMALE = "F"
    UNKNOWN = "U"


class Direction(Enum):
    """Direction enumeration for graph traversal."""
    LEFT = "left"
    RIGHT = "right"


# Default values
DEFAULT_FONT_SIZE = 10
DEFAULT_SYMBOL_SIZE = 25
DEFAULT_PAGE_MARGIN = 100
DEFAULT_HMARGIN = 20
DEFAULT_NODE_HEIGHT = 50

# Text calculation constants
BASE_FONT_WIDTH = 0.52
FONT_HEIGHT_MULTIPLIER = 1.2
TEXT_WIDTH_THRESHOLD = 1.8
TEXT_WIDTH_ADJUSTMENT = 0.2

# Connector overlap detection
MAX_OVERLAP_ITERATIONS = 100
OVERLAP_ADJUSTMENT_STEP = 8

# Default colors
DEFAULT_INDIVIDUAL_COLOR = "#F2E6D2"
DUPLICATE_CONNECTOR_COLOR = "#BAFFD2"
