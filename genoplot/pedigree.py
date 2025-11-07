# Copyright (c) 2016 by Welded Anvil Technologies (David D. Newell). All Rights Reserved.
# This software is the confidential and proprietary information of
# Welded Anvil Technologies (David D. Newell) ("Confidential Information").
# You shall not disclose such Confidential Information and shall use it
# only in accordance with the terms of the license agreement you entered
# into with Welded Anvil Technologies (David D. Newell).
# @author david@newell.at

import copy
import logging
import time

import gedcom

from .family import Family
from .individual import Individual

logger = logging.getLogger("genoplot")


class Pedigree:
    def __init__(self, name, gedcom_file, font_size=10, hmargin=0, **kwargs):
        """
        Pedigree - defines a pedigree built from a gedcom file

        :param name: Pedigree name/title
        :type name: str
        :param gedcom_file: GEDCOM file path
        :type gedcom_file: str
        """
        self.name = name
        self._gedcom = gedcom.parse(gedcom_file)
        self._individuals = {}
        self._families = {}
        self._parent_ids = set()
        self._children_ids = set()

        self._font_size = font_size
        self._hmargin = hmargin

        for k, v in kwargs.items():
            setattr(self, k, v)

        self._setup()

    def _setup(self):
        logger.debug("Processing individuals in GEDCOM")
        start = time.time()
        for individual in self._gedcom.individuals:
            try:
                i = Individual(individual, self, font_size=self._font_size)
            except Exception:
                logger.warn("Error adding individual: %s", individual)
                continue

            logger.debug(f"Adding individual: {i.name}")
            self._individuals[i.id] = i
        logger.info(f"Processing individuals took {time.time()-start:.4f}s")

        logger.debug("Processing families in GEDCOM")
        start = time.time()
        for family in self._gedcom.families:
            try:
                f = Family(family, self, font_size=self._font_size, hmargin=self._hmargin)
            except Exception:
                logger.warning(f"Error adding family: {family}")
                continue

            logger.debug(f"Adding family: {f.id}")
            self._families[f.id] = f
            for id in f.parent_ids():
                self._parent_ids.add(id)
            for id in f.children_ids():
                self._children_ids.add(id)
        logger.info(f"Processing families took {time.time()-start:.4f}s")
        logger.info(
            f"Parsing GEDCOM complete: {len(self._individuals)} individuals "
            f"and {len(self._families)} families found"
        )

    def __len__(self):
        """Returns number of individuals in pedigree"""
        return len(self._individuals)

    def duplicate_individual(self, individual):
        """Creates and returns duplicate of supplied individual"""
        if individual.id in self._individuals:
            duplicate = copy.copy(individual)
            duplicate.id = max(self._individuals) + 1
            self._individuals[duplicate.id] = duplicate
            for family in self.individual_families(individual.id, role="child"):
                family.add_child(duplicate.id)
            logger.debug(
                f"Created duplicate individual: {individual.name}\t"
                f"ID: {individual.id} -> {duplicate.id}"
            )
            return duplicate
        else:
            logger.warning(
                f"Creating duplicate individual not in pedigree: "
                f"{individual.id} - {individual.name}"
            )
            return copy.copy(individual)

    def is_parent(self, pid):
        """Returns whether specified individual ID is a parent in a family in this pedigree"""
        return pid in self._parent_ids

    def is_child(self, pid):
        """Returns whether specified individual ID is a child in a family in this pedigree"""
        return pid in self._children_ids

    def individual(self, pid):
        """Returns individual for specified individual ID

        :param pid: Individual ID
        :type pid: int
        """
        if pid not in self._individuals:
            logger.warning(f"Individual not found in pedigree: {pid}")
            return None
        else:
            return self._individuals[pid]

    def individual_families(self, pid, role="parent"):
        """Returns families in which specified individual ID belongs

        :param pid: Individual ID
        :type pid: int
        :param role: Role in family
        :type: str
        """
        if role == "parent":
            return [family for family in self._families.values() if family.contains_parent(pid)]
        elif role == "child":
            return [family for family in self._families.values() if family.contains_child(pid)]
        else:
            return [family for family in self._families.values() if pid in family]

    def family(self, fid):
        """Returns family for specified family ID

        :param fid: Family ID
        :type fid: int
        """
        if fid not in self._families:
            return None
        else:
            return self._families[fid]

    def families_with_parent(self, parents=None):
        """Returns families with parent IDs specified

        :param parents: Parent(s) to find in family
        :type parents: int or list
        """
        if parents is None:
            parents = []

        if isinstance(parents, int):
            return [
                family for family in self._families.values()
                if parents in family.parent_ids()
            ]
        elif isinstance(parents, list):
            f = None
            for parent in parents:
                if f is None:
                    f = set(self.families_with_parent(parent))
                else:
                    f.intersection_update(set(self.families_with_parent(parent)))
            return list(f)
        else:
            return []

    def vertices(self):
        """Returns families and individuals who comprise all vertices in family tree plot"""
        vertices = list(self._families.values())
        individual_keys = [individual for individual in self._individuals.values() if not individual.is_parent()]
        vertices.extend(individual_keys)
        return vertices


