# Copyright (c) 2016 by Welded Anvil Technologies (David D. Newell). All Rights Reserved.
# This software is the confidential and proprietary information of
# Welded Anvil Technologies (David D. Newell) ("Confidential Information").
# You shall not disclose such Confidential Information and shall use it
# only in accordance with the terms of the license agreement you entered
# into with Welded Anvil Technologies (David D. Newell).
# @author david@newell.at

"""Utility functions for the genoplot package."""

import logging
from typing import Generator, Optional, Tuple, Union

from .constants import (
    BASE_FONT_WIDTH,
    FONT_HEIGHT_MULTIPLIER,
    TEXT_WIDTH_ADJUSTMENT,
    TEXT_WIDTH_THRESHOLD,
)

logger = logging.getLogger("genoplot")


def calculate_text_size(
    text: Union[str, Generator[str, None, None], list[str]],
    font_size: int
) -> Tuple[float, float]:
    """Calculate the width and height of text at a given font size.

    Args:
        text: Text string or iterable of text strings to measure.
        font_size: Font size in points.

    Returns:
        A tuple of (width, height) where width is the maximum width
        of any text line and height is the sum of all line heights.

    Examples:
        >>> calculate_text_size("Hello", 12)
        (31.2, 14.4)
        >>> calculate_text_size(["Line 1", "Line 2"], 10)
        (31.2, 24.0)
    """
    if isinstance(text, str):
        text = [text]

    font_width = font_size * BASE_FONT_WIDTH

    width = []
    height = []

    for t in text:
        t_width = len(t) * font_width
        if t_width > TEXT_WIDTH_THRESHOLD:
            t_width += TEXT_WIDTH_ADJUSTMENT

        t_height = font_size * FONT_HEIGHT_MULTIPLIER

        width.append(t_width)
        height.append(t_height)

    return max(width, default=0), sum(height)


def strip_name(name: Optional[str]) -> Optional[str]:
    """Remove invalid characters from a name string.

    Args:
        name: Name string to clean, or None.

    Returns:
        Cleaned name string with tabs and commas replaced by spaces,
        and quotes/parentheses/periods removed. Returns None if input is None.

    Examples:
        >>> strip_name("O'Brien, John")
        'OBrien John'
        >>> strip_name(None)
        None
    """
    if not isinstance(name, str):
        return name

    invalid = "'\"(),."
    return "".join(
        c for c in name.replace("\t", " ").replace(",", " ")
        if c not in invalid
    )


# Deprecated alias for backward compatibility
stripName = strip_name

