# Copyright (c) 2016 by Welded Anvil Technologies (David D. Newell). All Rights Reserved.
# This software is the confidential and proprietary information of
# Welded Anvil Technologies (David D. Newell) ("Confidential Information").
# You shall not disclose such Confidential Information and shall use it
# only in accordance with the terms of the license agreement you entered
# into with Welded Anvil Technologies (David D. Newell).
# @author david@newell.at

"""Family class for representing family units in a pedigree."""

import logging
from typing import TYPE_CHECKING, Any, Optional, Tuple

from .constants import DEFAULT_HMARGIN
from .utils import calculate_text_size

if TYPE_CHECKING:
    from .individual import Individual
    from .pedigree import Pedigree

logger = logging.getLogger("genoplot")


class Family:
    """Represents a family unit (parents and children) in a pedigree.

    Attributes:
        id: Unique identifier for the family.
        x: X coordinate for graph layout.
        y: Y coordinate for graph layout.
        width: Calculated width for display.
        height: Calculated height for display.
    """

    def __init__(
        self,
        family: Any,
        pedigree: Optional['Pedigree'] = None,
        font_size: int = 10,
        hmargin: int = DEFAULT_HMARGIN,
        **kwargs: Any
    ) -> None:
        """Initialize a Family.

        Args:
            family: Raw GEDCOM parsed family object.
            pedigree: Pedigree object to which family belongs.
            font_size: Font size for text rendering.
            hmargin: Horizontal margin between parents.
            **kwargs: Additional attributes to set on the family.
        """
        self._raw: Any = family
        self._pedigree: Optional['Pedigree'] = pedigree
        self._father: Optional[int] = None
        self._mother: Optional[int] = None

        self._font_size: int = font_size
        self._hmargin: int = hmargin
        self.x: float = 0.0
        self.y: float = 0.0

        # Layout properties
        self.layout_number: int = 0
        self.layout_prelim: float = 0.0
        self.layout_mod: float = 0.0
        self.layout_change: float = 0.0
        self.layout_shift: float = 0.0
        self.layout_thread: Optional[Any] = None
        self.layout_ancestor: Optional[Any] = None
        self.layout_branch: Optional[int] = None

        # Set additional keyword arguments
        for k, v in kwargs.items():
            setattr(self, k, v)

        self._setup()
        self.width: float
        self.height: float
        self.width, self.height = self.size()

    def _setup(self):
        self.id = int(self._raw.id.replace("@", "").replace("F", ""))
        self._parent_ids = []
        self._children_ids = []
        for person in self._raw.partners:
            pid = int(person.value.replace("@", "").replace("P", ""))
            self._parent_ids.append(pid)
            if person.tag == "HUSB":
                self._father = pid
            elif person.tag == "WIFE":
                self._mother = pid

        for el in self._raw.child_elements:
            if el.tag == "CHIL":
                pid = int(el.value.replace("@", "").replace("P", ""))
                self._children_ids.append(pid)
        self._sort_children()

    def _sort_children(self):
        self._children_ids.sort(key=self._sort_by_birth)

    def _sort_by_birth(self, cid):
        child = self._pedigree.individual(cid)
        if cid is None or child is None:
            logger.critical(
                f"Individual {cid} does not exist, cannot continue "
                f"sorting children in family {self.id}"
            )
            return 0
        if child.birth is None:
            return 0
        elif isinstance(child.birth, str):
            return 0
        else:
            return child.birth

    def __repr__(self) -> str:
        """Return detailed string representation of Family."""
        return (
            f"Family(id={self.id}, father={self._father}, "
            f"mother={self._mother}, children={len(self._children_ids)})"
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"Family {self.id}"

    def add_child(self, pid: int) -> None:
        """Add a child to the family.

        Args:
            pid: Individual ID of the child to add.
        """
        self._children_ids.append(pid)
        self._sort_children()

    def set_coordinates(
        self,
        x: float,
        y: float,
        add_to_history: bool = False
    ) -> None:
        """Sets coordinates for parents

        :param x: Family x coordinate
        :type x: float
        :param y: Family y coordinate
        :type y: float
        """
        father = self.father()
        mother = self.mother()
        self.x = x
        self.y = y
        if father is not None:
            father.set_coordinates(x, y, add_to_history)
            fwidth = father.size()[0]
        else:
            fwidth = self._hmargin
        if mother is not None:
            mwidth = mother.size()[0]
            mx = x + fwidth/2 + mwidth/2 + self._hmargin*2
            mother.set_coordinates(mx, y, add_to_history)

    @property
    def father_id(self) -> Optional[int]:
        """Get father's individual ID.

        Returns:
            Father's ID or None if not present.
        """
        return self._father

    @property
    def mother_id(self) -> Optional[int]:
        """Get mother's individual ID.

        Returns:
            Mother's ID or None if not present.
        """
        return self._mother

    def father(self) -> Optional['Individual']:
        """Get father Individual object.

        Returns:
            Father Individual or None if not present.

        Raises:
            ValueError: If pedigree is not defined.
        """
        if self._pedigree is None:
            raise ValueError("Pedigree is not defined")
        if self._father is None:
            return None
        return self._pedigree.individual(self._father)

    def mother(self) -> Optional['Individual']:
        """Get mother Individual object.

        Returns:
            Mother Individual or None if not present.

        Raises:
            ValueError: If pedigree is not defined.
        """
        if self._pedigree is None:
            raise ValueError("Pedigree is not defined")
        if self._mother is None:
            return None
        return self._pedigree.individual(self._mother)

    def parent_count(self) -> int:
        """Get number of parents in family.

        Returns:
            Count of parents (0-2).
        """
        return len(self._parent_ids)

    def parent_ids(self) -> list[int]:
        """Get IDs of parents in family.

        Returns:
            List of parent individual IDs.
        """
        return self._parent_ids

    def parents(self) -> list['Individual']:
        """Get Individual objects for parents in family.

        Returns:
            List of parent Individual objects.

        Raises:
            ValueError: If pedigree is not defined.
        """
        if self._pedigree is None:
            raise ValueError("Pedigree is not defined")
        return [self._pedigree.individual(pid) for pid in self._parent_ids]

    def children_count(self) -> int:
        """Get number of children in family.

        Returns:
            Count of children.
        """
        return len(self._children_ids)

    def children_ids(self) -> list[int]:
        """Get IDs of children in family.

        Returns:
            List of child individual IDs.
        """
        return self._children_ids

    def children(self) -> list['Individual']:
        """Get Individual objects for children in family.

        Returns:
            List of child Individual objects sorted by birth date.

        Raises:
            ValueError: If pedigree is not defined.
        """
        if self._pedigree is None:
            raise ValueError("Pedigree is not defined")
        return [
            self._pedigree.individual(pid)
            for pid in sorted(self._children_ids, key=self._sort_by_birth)
        ]

    def contains_parent(self, pid: int) -> bool:
        """Check if specified ID is a parent in this family.

        Args:
            pid: Individual ID to check.

        Returns:
            True if ID is a parent in this family.
        """
        return pid in self._parent_ids

    def contains_child(self, pid: int) -> bool:
        """Check if specified ID is a child in this family.

        Args:
            pid: Individual ID to check.

        Returns:
            True if ID is a child in this family.
        """
        return pid in self._children_ids

    def __contains__(self, pid: int) -> bool:
        """Check if specified ID is in this family (parent or child).

        Args:
            pid: Individual ID to check.

        Returns:
            True if ID is in this family.
        """
        return self.contains_child(pid) or self.contains_parent(pid)

    def size(self) -> Tuple[float, float]:
        """
        Returns label size of indivdual at specified font size

        :param font_size: Font size for which to calculate size
        :type font_size: float
        :param hmargin: Horizontal margin
        :type hmargin: float
        """
        height = 0
        width = 0

        mother = self.mother()
        father = self.father()

        for parent in self.parents():
            if parent is not None:
                pw, ph = parent.size()
                width += pw
                height += ph

        if width > 0:
            width += self._hmargin*2

        return width, height

