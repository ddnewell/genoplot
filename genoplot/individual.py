# Copyright (c) 2016 by Welded Anvil Technologies (David D. Newell). All Rights Reserved.
# This software is the confidential and proprietary information of
# Welded Anvil Technologies (David D. Newell) ("Confidential Information").
# You shall not disclose such Confidential Information and shall use it
# only in accordance with the terms of the license agreement you entered
# into with Welded Anvil Technologies (David D. Newell).
# @author david@newell.at

import logging

import dateparser

from .utils import calculate_text_size, stripName

logger = logging.getLogger("genoplot")


class Individual:
    def __init__(self, individual, pedigree=None, output_fields=None, font_size=10, **kwargs):
        """
        Individual - defines a  in a pedigree
        :param individual: Raw Gedcom parsed individual
        :type individual: object
        :param pedigree: Pedigree object to which individual belongs
        :type pedigree: object
        :param output_fields: Fields to show
        :type output_fields: list
        """
        self._raw = individual
        self._pedigree = pedigree
        self.x = 0
        self.y = 0
        self.name = ""
        self._color = "#F2E6D2"
        self._coordinates = set()
        if output_fields is None:
            self._output_fields = [
                "layout_branch", "layout_number", "layout_family",
                "layout_ancestor", "layout_prelims", "layout_shifts",
                "layout_mods", "id", "name"
            ]
        else:
            self._output_fields = output_fields

        self._font_size = font_size

        self.layout_number = 0
        self.layout_prelim = 0
        self.layout_mod = 0
        self.layout_change = 0
        self.layout_shift = 0
        self.layout_thread = None
        self.layout_ancestor = None
        self.layout_family = None
        self.layout_branch = None

        for k, v in kwargs.items():
            setattr(self, k, v)

        self._setup()
        self.width, self.height = self.size()

    def _setup(self):
        self.id = int(self._raw.id.replace("@", "").replace("P", ""))
        self.first, self.last = self._raw.name
        if self.last is not None:
            name = self.last
        else:
            name = ""
        if self.first is not None and len(self.first) > 0:
            name = self.first + " " + name

        self.name = stripName(name)
        self.first = stripName(self.first)
        self.last = stripName(self.last)

        try:
            self.sex = self._raw.sex
        except AttributeError:
            self.sex = "U"

        try:
            self.mother = int(self._raw.mother.id.replace("@", "").replace("P", ""))
        except AttributeError:
            self.mother = None

        try:
            self.father = int(self._raw.father.id.replace("@", "").replace("P", ""))
        except AttributeError:
            self.father = None

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

        self._customAttrs = []

    def is_parent(self):
        """Returns whether individual is a parent in this pedigree"""
        if self._pedigree is None:
            raise Exception("Pedigree is not defined")
        return self._pedigree.is_parent(self.id)

    def is_child(self):
        """Returns whether individual is a child in this pedigree"""
        if self._pedigree is None:
            raise Exception("Pedigree is not defined")
        return self._pedigree.is_child(self.id)

    def families(self, role="parent"):
        """Returns families in which individual belongs

        :param role: Role in family
        :type: str
        """
        if self._pedigree is None:
            raise Exception("Pedigree is not defined")
        return self._pedigree.individual_families(self.id, role)

    def size(self):
        """
        Returns label size of indivdual at the font size specified during object creation
        """
        return calculate_text_size(self.output_text(), self._font_size)

    def output_text(self):
        """Text to print on pedigree"""
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

    def color(self):
        """Returns color to draw the individual on the pedigree"""
        return self._color

    def set_coordinates(self, x, y, add_to_history=True):
        """Sets x coordinate with history"""
        self.x = x
        self.y = y
        if add_to_history:
            self._coordinates.add((x, y))

    def coordinate_history(self):
        """Returns all coordinates specified for individual"""
        return self._coordinates
