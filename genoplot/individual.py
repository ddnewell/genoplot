# Copyright (c) 2016 by Welded Anvil Technologies (David D. Newell). All Rights Reserved.
# This software is the confidential and proprietary information of
# Welded Anvil Technologies (David D. Newell) ("Confidential Information").
# You shall not disclose such Confidential Information and shall use it
# only in accordance with the terms of the license agreement you entered
# into with Welded Anvil Technologies (David D. Newell).
# @author david@newell.at

"""Individual class for representing people in a pedigree."""

import logging
from typing import TYPE_CHECKING, Any, Generator, Optional, Set, Tuple

import dateparser

from .constants import DEFAULT_INDIVIDUAL_COLOR, Sex
from .exceptions import GedcomParseError
from .utils import calculate_text_size, strip_name

if TYPE_CHECKING:
    from .pedigree import Pedigree
    from .family import Family

logger = logging.getLogger("genoplot")


class Individual:
    """Represents an individual person in a pedigree.

    Attributes:
        id: Unique identifier for the individual.
        name: Full name of the individual.
        first: First name.
        last: Last name.
        sex: Biological sex (M/F/U).
        birth: Birth date in ISO format (YYYY-MM-DD).
        death: Death date in ISO format (YYYY-MM-DD).
        mother: ID of mother individual, if known.
        father: ID of father individual, if known.
        x: X coordinate for graph layout.
        y: Y coordinate for graph layout.
        width: Calculated width for display.
        height: Calculated height for display.
    """

    def __init__(
        self,
        individual: Any,
        pedigree: Optional['Pedigree'] = None,
        output_fields: Optional[list[str]] = None,
        font_size: int = 10,
        **kwargs: Any
    ) -> None:
        """Initialize an Individual.

        Args:
            individual: Raw GEDCOM parsed individual object.
            pedigree: Pedigree object to which individual belongs.
            output_fields: List of field names to include in output text.
            font_size: Font size for text rendering.
            **kwargs: Additional attributes to set on the individual.
        """
        self._raw: Any = individual
        self._pedigree: Optional['Pedigree'] = pedigree
        self.x: float = 0.0
        self.y: float = 0.0
        self.name: str = ""
        self._color: str = DEFAULT_INDIVIDUAL_COLOR
        self._coordinates: Set[Tuple[float, float]] = set()
        self._output_fields: list[str] = output_fields or [
            "layout_branch", "layout_number", "layout_family",
            "layout_ancestor", "layout_prelims", "layout_shifts",
            "layout_mods", "id", "name"
        ]

        self._font_size: int = font_size

        # Layout properties
        self.layout_number: int = 0
        self.layout_prelim: float = 0.0
        self.layout_mod: float = 0.0
        self.layout_change: float = 0.0
        self.layout_shift: float = 0.0
        self.layout_thread: Optional[Any] = None
        self.layout_ancestor: Optional[Any] = None
        self.layout_family: Optional[Any] = None
        self.layout_branch: Optional[int] = None

        # Set additional keyword arguments
        for k, v in kwargs.items():
            setattr(self, k, v)

        self._setup()
        self.width: float
        self.height: float
        self.width, self.height = self.size()

    def _setup(self) -> None:
        """Set up individual attributes from raw GEDCOM data."""
        try:
            self.id: int = int(self._raw.id.replace("@", "").replace("P", ""))
        except (ValueError, AttributeError) as e:
            raise GedcomParseError(f"Invalid individual ID format: {self._raw.id}") from e
        self.first: Optional[str]
        self.last: Optional[str]
        self.first, self.last = self._raw.name

        # Build full name
        name = self.last if self.last is not None else ""
        if self.first is not None and len(self.first) > 0:
            name = f"{self.first} {name}"

        self.name = strip_name(name) or ""
        self.first = strip_name(self.first)
        self.last = strip_name(self.last)

        # Use getattr for safer attribute access
        self.sex: str = getattr(self._raw, 'sex', Sex.UNKNOWN.value)

        # Handle mother and father references
        self.mother: Optional[int] = None
        if hasattr(self._raw, 'mother') and self._raw.mother:
            self.mother = int(self._raw.mother.id.replace("@", "").replace("P", ""))

        self.father: Optional[int] = None
        if hasattr(self._raw, 'father') and self._raw.father:
            self.father = int(self._raw.father.id.replace("@", "").replace("P", ""))

        try:
            if isinstance(self._raw.birth, list):
                birth = self._raw.birth[0]
            else:
                birth = self._raw.birth
            bdate = birth.date
            self.birthDate = f"* {bdate}".strip()
            self.birthPlace = birth.place.strip()
            if "abt" in bdate.lower():
                bdate = bdate.strip("abtABT. ")
            if "aft" in bdate.lower():
                bdate = bdate.strip("aftAFT. ")
            if "bef" in bdate.lower():
                bdate = bdate.strip("befBEF. ")
            if "~" in bdate:
                bdate = bdate.strip("~ ")
            parsedBdate = dateparser.parse(bdate)
            if parsedBdate is None:
                self.birth = bdate
            else:
                self.birth = parsedBdate.strftime("%Y-%m-%d")
        except (AttributeError, IndexError, TypeError):
            self.birth = None
            self.birthDate = None
            self.birthPlace = None

        try:
            if isinstance(self._raw.death, list):
                death = self._raw.death[0]
            else:
                death = self._raw.death
            ddate = death.date
            self.deathDate = f"✝ {ddate}".strip()
            self.deathPlace = death.place.strip()
            if "abt" in ddate.lower():
                ddate = ddate.strip("abtABT. ")
            if "aft" in ddate.lower():
                ddate = ddate.strip("aftAFT. ")
            if "bef" in ddate.lower():
                ddate = ddate.strip("befBEF. ")
            if "~" in ddate:
                ddate = ddate.strip("~ ")
            parsedDdate = dateparser.parse(ddate)
            if parsedDdate is None:
                self.death = ddate
            else:
                self.death = parsedDdate.strftime("%Y-%m-%d")
        except (AttributeError, IndexError, TypeError):
            self.death = None
            self.deathDate = None
            self.deathPlace = None

        self._customAttrs: list[Any] = []

    def __repr__(self) -> str:
        """Return detailed string representation of Individual."""
        return (
            f"Individual(id={self.id}, name={self.name!r}, "
            f"sex={self.sex!r}, birth={self.birth!r}, death={self.death!r})"
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"{self.name} (ID: {self.id})"

    def is_parent(self) -> bool:
        """Check if individual is a parent in this pedigree.

        Returns:
            True if individual is a parent, False otherwise.

        Raises:
            ValueError: If pedigree is not defined.
        """
        if self._pedigree is None:
            raise ValueError("Pedigree is not defined")
        return self._pedigree.is_parent(self.id)

    def is_child(self) -> bool:
        """Check if individual is a child in this pedigree.

        Returns:
            True if individual is a child, False otherwise.

        Raises:
            ValueError: If pedigree is not defined.
        """
        if self._pedigree is None:
            raise ValueError("Pedigree is not defined")
        return self._pedigree.is_child(self.id)

    def families(self, role: str = "parent") -> list['Family']:
        """Get families in which individual belongs.

        Args:
            role: Role in family ('parent', 'child', or 'any').

        Returns:
            List of Family objects.

        Raises:
            ValueError: If pedigree is not defined.
        """
        if self._pedigree is None:
            raise ValueError("Pedigree is not defined")
        return self._pedigree.individual_families(self.id, role)

    def size(self) -> Tuple[float, float]:
        """Calculate display size based on output text.

        Returns:
            Tuple of (width, height) in pixels.
        """
        return calculate_text_size(self.output_text(), self._font_size)

    def output_text(self) -> Generator[str, None, None]:
        """Generate text lines to print on pedigree.

        Yields:
            String values for each output field.
        """
        families = self.families()
        self.layout_prelims = ["Prelim", int(self.layout_prelim)]
        self.layout_shifts = ["Shift", int(self.layout_shift)]
        self.layout_mods = ["Mod", int(self.layout_mod)]
        if len(families) > 0:
            self.layout_number = ["#"]
            self.layout_ancestor = ["Anc"]
            self.layout_family = ["Fam"]
            self.layout_branch = ["Br"]
            for fam in families:
                self.layout_number.append(fam.layout_number)
                self.layout_ancestor.append(fam.layout_ancestor)
                self.layout_family.append(f"F{fam.id}")
                self.layout_branch.append(fam.layout_branch)
                self.layout_prelims.append(int(fam.layout_prelim))
                self.layout_shifts.append(int(fam.layout_shift))
                self.layout_mods.append(int(fam.layout_mod))
        return (str(getattr(self, k)) for k in self._output_fields)

    @property
    def color(self) -> str:
        """Get color to draw the individual on the pedigree.

        Returns:
            Hex color code as string.
        """
        return self._color

    def set_coordinates(
        self,
        x: float,
        y: float,
        add_to_history: bool = True
    ) -> None:
        """Set individual's coordinates.

        Args:
            x: X coordinate.
            y: Y coordinate.
            add_to_history: Whether to add coordinates to history.
        """
        self.x = x
        self.y = y
        if add_to_history:
            self._coordinates.add((x, y))

    def coordinate_history(self) -> Set[Tuple[float, float]]:
        """Get all historical coordinates for this individual.

        Returns:
            Set of (x, y) coordinate tuples.
        """
        return self._coordinates
