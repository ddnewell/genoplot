# Copyright (c) 2016 by Welded Anvil Technologies (David D. Newell). All Rights Reserved.
# This software is the confidential and proprietary information of
# Welded Anvil Technologies (David D. Newell) ("Confidential Information").
# You shall not disclose such Confidential Information and shall use it
# only in accordance with the terms of the license agreement you entered
# into with Welded Anvil Technologies (David D. Newell).
# @author david@newell.at

import itertools
import logging
import sys
import time
import traceback

import networkx as nx
import pygraphviz

from . import buchheim
from .family import Family
from .pedigree import Pedigree
from .utils import calculate_text_size

logger = logging.getLogger("genoplot")


class Branch:
    def __init__(self, id, subgraph, parent, font_size, hmargin=10, node_height=50):
        """
        Branch - defines a branch within the family graph

        """
        self.id = id
        self._graph = subgraph
        self.parent = parent
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.hmargin = hmargin
        self.node_height = node_height
        self.font_size = font_size
        self._extremes = [None]*4

        for node in self._graph.nodes():
            self._graph.nodes[node]["el"].layout_branch = id

    def __len__(self):
        return len(self._graph)

    def __contains__(self, node):
        return node in self._graph

    def layout(self):
        # Get first node
        v = None
        for vid, deg in self._graph.in_degree():
            if deg == 0:
                v = vid
                break
        if v is None:
            logger.critical(f"Could not find parent node to layout branch {self.id}: stopping")
            exit(1)

        post_order = list(nx.dfs_postorder_nodes(self._graph, v))

        logger.debug(f"<Branch {self.id}> First Element: {v}; post-order: {post_order}")
        heights = self.layout_preprocessing(v)
        self.layout_first_walk(v)

        self._extremes = [None]*4

        self.layout_second_walk(
            v, -self._graph.nodes[v]["el"].layout_prelim, depth=0,
            height=self.node_height+max(heights)
        )

        # Update coordinates
        dx = dy = 0
        if not self._extremes[0] == 0:
            dx = -self._extremes[0]
        if not self._extremes[2] == 0:
            dy = -self._extremes[2]
        if dx == 0 and dy == 0:
            logger.debug(f"<Branch {self.id}> Extremes after initial layout: {self._extremes}")
        else:
            logger.debug(
                f"<Branch {self.id}> Extremes after initial layout: {self._extremes}    "
                f"dx: {dx:.2f}  dy: {dy:.2f}"
            )
            self._extremes = [None]*4
            for vid, data in self._graph.nodes(data=True):
                el = data["el"]
                el.x += dx
                el.y += dy
                if self._extremes[0] is None or el.x < self._extremes[0]:
                    self._extremes[0] = el.x
                if self._extremes[1] is None or el.x > self._extremes[1]:
                    self._extremes[1] = el.x
                if self._extremes[2] is None or el.y < self._extremes[2]:
                    self._extremes[2] = el.y
                if self._extremes[3] is None or el.y > self._extremes[3]:
                    self._extremes[3] = el.y
            logger.debug(f"<Branch {self.id}> Extremes after adjustment: {self._extremes}")
        # Update branch size
        self.width = self._extremes[1] - self._extremes[0]
        self.height = self._extremes[3] - self._extremes[2]

    def layout_preprocessing(self, v, prev=None, n=1, lmost_sibling=None, lsibling=None):
        el = self._graph.nodes[v]["el"]
        el.layout_ancestor = prev
        el.layout_number = n
        el.layout_lmost_sibling = lmost_sibling
        el.layout_lsibling = lsibling
        el.layout_thread = None
        heights = [el.height]
        self._graph.nodes[v]["children"] = tuple(
            sorted(self._graph[v].keys(), key=self._sort_children)
        )
        for n, child in enumerate(self._graph.nodes[v]["children"]):
            lsibling = self._graph.nodes[v]["children"][n-1] if n > 0 else None
            # TODO: verify that we don't need to set self to left most sibling
            lmost_sibling = self._graph.nodes[v]["children"][0] if n > 0 else None
            child_heights = self.layout_preprocessing(child, v, n+1, lmost_sibling, lsibling)
            heights.extend(child_heights)
        return heights

    def _reconcile_birth_date(self, bdate):
        if bdate is None:
            return 0
        elif isinstance(bdate, str):
            return 0
        else:
            return bdate

    def _sort_children(self, v):
        n = self._graph.nodes[v]
        if n is None:
            logger.critical(
                f"Node {v} does not exist, cannot continue sorting children in layout"
            )
        in_edges = self._graph.in_edges(v)
        if len(in_edges) == 0:
            logger.critical(
                f"No edges into node {v}, cannot continue sorting children in layout"
            )
        parent_el = self._graph.nodes[in_edges[0][0]]["el"]
        tgt = n["el"]
        if tgt is None:
            logger.error(f"Could not populate node for ID: {v}")
            return 0

        if isinstance(tgt, Family):
            tgt_father = tgt.father()
            tgt_mother = tgt.mother()
            if tgt_father is None and tgt_mother is None:
                logger.critical(
                    f"Empty parents found in family while sorting children; "
                    f"cannot continue, family ID: {tgt.id}"
                )
                exit(1)

            if tgt_father is None and tgt_mother is not None:
                return self._reconcile_birth_date(tgt_mother.birth)
            elif tgt_father is not None and tgt_mother is None:
                return self._reconcile_birth_date(tgt_father.birth)

            if isinstance(parent_el, Family):
                # Family to family link
                src_father = parent_el.father()
                src_mother = parent_el.mother()

                for s, t in itertools.product((src_father, src_mother), (tgt_father, tgt_mother)):
                    if s is None or t is None:
                        continue
                    if self.parent.is_consanguineous(s.id, t.id):
                        return self._reconcile_birth_date(t.birth)
            else:
                # Individual to family link
                if self.parent.is_consanguineous(parent_el.id, tgt_father.id):
                    return self._reconcile_birth_date(tgt_father.birth)
                else:
                    return self._reconcile_birth_date(tgt_mother.birth)
        else:
            return self._reconcile_birth_date(tgt.birth)

        return 0

    def layout_first_walk(self, v):
        el = self._graph.nodes[v]["el"]
        if "children" in self._graph.nodes[v] and len(self._graph.nodes[v]["children"]) > 0:
            children = self._graph.nodes[v]["children"]
            default_ancestor = children[0]
            for child in children:
                self.layout_first_walk(child)
                default_ancestor = self.layout_apportion(child, default_ancestor)
            self.layout_execute_shift(v)
            first_child = self._graph.nodes[children[0]]["el"]
            last_child = self._graph.nodes[children[-1]]["el"]
            midpoint = (
                first_child.layout_prelim + last_child.layout_prelim +
                last_child.size()[0]
            ) / 2
            midpoint -= el.size()[0] / 2
            if el.layout_lsibling is not None:
                left_sibling = self._graph.nodes[el.layout_lsibling]["el"]
                el.layout_prelim = (
                    left_sibling.layout_prelim + left_sibling.size()[0] + self.hmargin
                )
                el.layout_mod = el.layout_prelim - midpoint
            else:
                el.layout_prelim = midpoint
        else:
            if el.layout_lmost_sibling is not None:
                left_sibling = self._graph.nodes[el.layout_lsibling]["el"]
                el.layout_prelim = (
                    left_sibling.layout_prelim + left_sibling.size()[0] + self.hmargin
                )
            else:
                el.layout_prelim = 0

        logger.debug(
            f"<Branch {self.id}> Element: {v} prelim: {el.layout_prelim:.1f}, "
            f"mod: {el.layout_mod:.1f}, change: {el.layout_change:.1f}"
        )

    def layout_apportion(self, v, default_ancestor):
        # o = outside, i = inside, l/- = left, r/+ = right
        # v = vertex
        # s = sum(vertex mod properties)
        el = self._graph.nodes[v]["el"]
        left_sibling = el.layout_lsibling
        logger.debug(f"<Branch {self.id}> layout_apportion - older_sibling: {left_sibling}")
        if left_sibling is not None:
            vir = vor = v
            vil = left_sibling
            vol = el.layout_lmost_sibling
            sir = sor = el.layout_mod

            vil_el = self._graph.nodes[vil]["el"]
            vir_el = self._graph.nodes[vir]["el"]
            vol_el = self._graph.nodes[vol]["el"]
            vor_el = self._graph.nodes[vor]["el"]

            sil = vil_el.layout_mod
            sol = vol_el.layout_mod

            loop_i = 0

            while (self.layout_next_element(vil, direction="right") is not None and
                    self.layout_next_element(vir, direction="left") is not None):

                vil = self.layout_next_element(vil, direction="right")
                vir = self.layout_next_element(vir, direction="left")
                vol = self.layout_next_element(vol, direction="left")
                vor = self.layout_next_element(vor, direction="right")

                vil_el = self._graph.nodes[vil]["el"]
                vir_el = self._graph.nodes[vir]["el"]
                vol_el = self._graph.nodes[vol]["el"]
                vor_el = self._graph.nodes[vor]["el"]

                vor_el.layout_ancestor = v

                width = vir_el.size()[0] + self.hmargin * 2
                shift = (vil_el.layout_prelim + sil) - (vir_el.layout_prelim + sir) + width
                logger.info(f"<Branch {self.id}> Loop #{loop_i}... shift: {shift}")
                if shift > 0:
                    local_ancestor = self.layout_left_ancestor(vil, v, default_ancestor)
                    self.layout_move_subtree(local_ancestor, v, shift)
                    sir += shift
                    sor += shift

                sil += vil_el.layout_mod
                sir += vir_el.layout_mod
                # if not vol is None:
                sol += vol_el.layout_mod
                # if not vor is None:
                sor += vor_el.layout_mod

            vil_next_right = self.layout_next_element(vil, direction="right")
            if (vil_next_right is not None and
                    self.layout_next_element(vor, direction="right") is None):
                logger.debug(f"<Branch {self.id}> Setting thread from {vor} to {vil_next_right}")
                vor_el.layout_thread = vil_next_right
                vor_el.layout_mod += sil - sor
            else:
                vir_next_left = self.layout_next_element(vir, direction="left")
                if (vir_next_left is not None and
                        self.layout_next_element(vol, direction="left") is None):
                    logger.debug(f"<Branch {self.id}> Setting thread from {vol} to {vir_next_left}")
                    vol_el.layout_thread = vir_next_left
                    vol_el.layout_mod += sir - sol
                default_ancestor = v

        return default_ancestor

    def layout_oldest_sibling(self, v):
        logger.debug(f"<Branch {self.id}> layout_oldest_sibling - v: {v}")
        if "children" in self._graph.nodes[v]:
            return self._graph.nodes[v]["children"][0]
        return None

    def layout_left_sibling(self, v):
        logger.debug(f"<Branch {self.id}> layout_left_sibling - v: {v}")
        in_edges = self._graph.in_edges(nbunch=(v))
        if len(in_edges) > 0:
            parent = in_edges[0][0]
            if ("children" in self._graph.nodes[parent] and
                        len(self._graph.nodes[parent]["children"]) > 0 and
                        v in self._graph.nodes[parent]["children"]):
                index = self._graph.nodes[parent]["children"].index(v)
                if index > 0:
                    return self._graph.nodes[parent]["children"][index-1]
        return None

    def layout_next_element(self, v, direction="left"):
        logger.debug(f"<Branch {self.id}> layout_next_element - Element: {v} direction: {direction}")
        if not self._graph.has_node(v):
            logger.error(f"<Branch {self.id}> layout_next_element - Graph does not contain node: {v}")
            return None
        elif "children" in self._graph.nodes[v] and len(self._graph.nodes[v]["children"]) > 0:
            if direction == "left":
                index = 0
            elif direction == "right":
                index = -1
            else:
                index = 0
            logger.debug(
                f"<Branch {self.id}> layout_next_element - Element: {v} returning "
                f"{direction} child at index {index}: {self._graph.nodes[v]['children'][index]}"
            )
            return self._graph.nodes[v]["children"][index]
        else:
            logger.debug(
                f"<Branch {self.id}> layout_next_element - Element: {v} returning "
                f"thread: {self._graph.nodes[v]['el'].layout_thread}"
            )
            return self._graph.nodes[v]["el"].layout_thread

    def layout_move_subtree(self, vl, vr, shift):
        # l/- = left, r/+ = right
        # v = vertex
        vr_el = self._graph.nodes[vr]["el"]
        vl_el = self._graph.nodes[vl]["el"]
        subtrees = vr_el.layout_number - vl_el.layout_number
        logger.info(
            f"<Branch {self.id}> layout_move_subtree - vl: {vl}, vr: {vr}, "
            f"shift: {shift:.2f}, subtrees: {subtrees}"
        )
        vr_el.layout_change -= shift / subtrees
        vr_el.layout_shift += shift
        vl_el.layout_change -= shift / subtrees
        vr_el.layout_prelim += shift
        vr_el.layout_mod += shift

    def layout_execute_shift(self, v):
        if "children" in self._graph.nodes[v]:
            logger.debug(f"<Branch {self.id}, node {v}> Executing shift")
            shift = 0
            change = 0
            for child in reversed(self._graph.nodes[v]["children"]):
                child_el = self._graph.nodes[child]["el"]
                child_el.layout_prelim += shift
                child_el.layout_mod += shift
                change += child_el.layout_change
                shift += child_el.layout_shift + change

    def layout_left_ancestor(self, vil, v, default_ancestor):
        logger.info(
            f"<Branch {self.id}> layout_left_ancestor - vil: {vil}  "
            f"v: {v}  default_ancestor: {default_ancestor}"
        )
        if self._graph.has_node(vil):
            vil_ancestor = self._graph.nodes[vil]["el"].layout_ancestor
            if vil_ancestor is not None:
                in_edges = self._graph.in_edges(nbunch=[vil_ancestor])
                if len(in_edges) > 0:
                    parent = in_edges[0][0]
                    if ("children" in self._graph.nodes[parent] and
                            len(self._graph.nodes[parent]["children"])):
                        if v in self._graph.nodes[parent]["children"]:
                            return vil_ancestor
        return default_ancestor

    def layout_second_walk(self, v, shift, depth, height=0):
        el = self._graph.nodes[v]["el"]
        el.x = el.layout_prelim + shift
        el.y = depth
        logger.debug(f"<Branch {self.id}> Element: {v} ({el.x:.1f}, {el.y:.1f})")
        logger.debug(
            f"<Branch {self.id}> Element: {v} ({el.x:.1f}, {el.y:.1f}) "
            f"prelim: {el.layout_prelim:.1f}, mod: {el.layout_mod:.1f}, "
            f"change: {el.layout_change:.1f}"
        )
        if self._extremes[0] is None or el.x < self._extremes[0]:
            self._extremes[0] = el.x
        if self._extremes[1] is None or el.x > self._extremes[1]:
            self._extremes[1] = el.x
        if self._extremes[2] is None or el.y < self._extremes[2]:
            self._extremes[2] = el.y
        if self._extremes[3] is None or el.y > self._extremes[3]:
            self._extremes[3] = el.y
        if "children" in self._graph.nodes[v]:
            for child in self._graph.nodes[v]["children"]:
                self.layout_second_walk(child, shift + el.layout_mod, depth + height, height)

    def set_coordinates(self, x, y):
        """Sets coordinates for branch and applies changes to all nodes"""
        dx = x - self.x
        dy = y - self.y
        self.x = x
        self.y = y

        self._extremes = [None]*4

        for vid, data in self._graph.nodes(data=True):
            el = data["el"]
            el.x += dx
            el.y += dy
            if self._extremes[0] is None or el.x < self._extremes[0]:
                self._extremes[0] = el.x
            if self._extremes[1] is None or el.x > self._extremes[1]:
                self._extremes[1] = el.x
            if self._extremes[2] is None or el.y < self._extremes[2]:
                self._extremes[2] = el.y
            if self._extremes[3] is None or el.y > self._extremes[3]:
                self._extremes[3] = el.y

    def persist_coordinates(self):
        """Sets coordinates for branch and applies changes to all nodes"""
        for vid, data in self._graph.nodes(data=True):
            data["el"].set_coordinates(data["el"].x, data["el"].y, add_to_history=True)

    def extremes(self):
        """Returns coordinate extremes for branch"""
        return self._extremes

    def size(self):
        """Returns overall width and height for branch"""
        return self.width, self.height


class FamilyGraph:
    def __init__(self, pedigree, font_size, hmargin=10, node_height=50, page_margin=10):
        self._pedigree = pedigree
        self.hmargin = hmargin
        self.node_height = node_height
        self.page_margin = page_margin
        self.font_size = font_size
        self._branches = []
        self._duplicate_people = set()
        self._graph = None
        self._branched_graph = None
        self._undirected_graph = None
        self._branch_links = set()
        self._create()
        self._layout()

    def has_node(self, node):
        return self._branched_graph.has_node(node)

    def has_edge(self, u, v):
        return self._branched_graph.has_edge(u, v)

    def extremes(self):
        """Returns coordinate extremes for familygraph"""
        extremes = [None]*4
        for branch in self._branches:
            bext = branch.extremes()
            for i in range(4):
                if bext[i] is None: #TODO
                    continue
                if extremes[i] is None or (i%2 == 0 and bext[i] < extremes[i]) or (bext[i] > extremes[i]):
                    extremes[i] = bext[i]
        return extremes

    def is_consanguineous(self, pid1, pid2):
        """Returns whether the specified individual IDs share a bloodline"""
        # Check for basic path between individuals, otherwise have to look at families
        graph_pid1 = "P{0}".format(pid1)
        graph_pid2 = "P{0}".format(pid2)
        if graph_pid1 in self._undirected_graph and \
                    graph_pid2 in self._undirected_graph and \
                    nx.has_path(self._undirected_graph, graph_pid1, graph_pid2):
            return True
        # Get individuals
        p1 = self._pedigree.individual(pid1)
        p2 = self._pedigree.individual(pid2)

        if graph_pid1 not in self._undirected_graph and graph_pid2 in self._undirected_graph:
            # Get first person's families
            f1 = ["F{0}".format(family.id) for family in p1.families()]
            # Check for path from first person's families to second person
            if any(nx.has_path(self._undirected_graph, f, graph_pid2) for f in f1 if f in self._undirected_graph):
                return True

        if graph_pid1 in self._undirected_graph and graph_pid2 not in self._undirected_graph:
            # Get second person's families
            f2 = ["F{0}".format(family.id) for family in p2.families()]
            # Check for path from first person families to second person
            if any(nx.has_path(self._undirected_graph, f, graph_pid1) for f in f2 if f in self._undirected_graph):
                return True

        if graph_pid1 not in self._undirected_graph and graph_pid2 not in self._undirected_graph:
            # Get families
            f1 = ["F{0}".format(family.id) for family in p1.families()]
            f2 = ["F{0}".format(family.id) for family in p2.families()]
            # If if one of the individuals has no families, don't continue
            if len(f1) == 0 or len(f2) == 0:
                return False
            # Check for paths between combinations of families, otherwise, individuals are not consanguineous
            return any(nx.has_path(self._undirected_graph, family1, family2)
                        for family1, family2 in itertools.product(f1, f2)
                        if family1 in self._undirected_graph and family2 in self._undirected_graph)

        return False

    def items(self):
        return self._branched_graph.nodes(data=True)

    def branch_links(self):
        return self._branch_links

    def duplicate_individuals(self):
        return self._duplicate_people

    def node(self, id):
        try:
            return self._branched_graph.nodes[id]
        except (KeyError, AttributeError):
            logger.warning(f"Could not retrieve {id} node from familygraph")
            return None

    def _create(self):
        """Returns NetworkX directed graph of vertices in pedigree"""
        logger.info("Creating family graph")
        create_start = time.time()
        self._graph = nx.DiGraph()

        vertices = {}
        self._branch_links = set()

        # Create vertices
        for el in self._pedigree.vertices():
            if type(el) is Family:
                vid = "F{0}".format(el.id)
            else:
                vid = "P{0}".format(el.id)
            # Add node to graph
            self._graph.add_node(vid, el=el)
            vertices[vid] = el

        for vid, v in vertices.items():
            logger.debug("Adding vertex %s of type %s", vid, type(v))
            if type(v) is Family:
                # Note: don't have to reach up to parent's families because they are captured in another family's down edges
                # A family typed vertex has children, which may be in families
                logger.debug("Family has %i children", v.children_count())
                children = v.children()
                for child in children:
                    if child.is_parent():
                        logger.debug("Child is parent: %s", child.id)
                        for family in self._pedigree.families_with_parent(child.id):
                            fid = "F{0}".format(family.id)
                            self._graph.add_edge(vid, fid, link="standard")
                            # self._graph.node[fid]["sibling"] = children.index(child)
                            logger.debug("Adding edge %s to %s", vid, fid)
                    else:
                        cid = "P{0}".format(child.id)
                        self._graph.add_edge(vid, cid, link="standard")
                        # self._graph.node[cid]["sibling"] = children.index(child)
                        logger.debug("Adding edge %s to %s", vid, cid)
            else:
                # An individual typed vertex does not have any children; get family for edges into vertex
                mother = v.mother
                father = v.father

                if mother is None and father is None:
                    continue
                elif mother is None:
                    families = self._pedigree.families_with_parent(mother)
                elif father is None:
                    families = self._pedigree.families_with_parent(father)
                else:
                    families = self._pedigree.families_with_parent([mother, father])

                logger.debug("Number of families for vertex %s: %i", vid, len(families))

                for family in families:
                    self._graph.add_edge("F{0}".format(family.id), vid, link="standard")
                    logger.debug("Adding edge %s to %s", "F{0}".format(family.id), vid)

        # Create branched graph
        self._branched_graph = nx.maximum_branching(self._graph)

        for v, d in self._graph.nodes(data=True):
            for k, val in d.items():
                self._branched_graph.nodes[v][k] = val

        # Add duplicate children to support cross-branch links
        removed_edges = set(self._graph.edges()) - set(self._branched_graph.edges())
        for (nid1, nid2) in removed_edges:
            # Update original graph
            self._graph[nid1][nid2]["link"] = "branch"
            # Create cross-branch links
            if nid2[0] == "F":
                children = self._pedigree.family(int(nid2[1:])).parents()
            else:
                children = [self._pedigree.individual(int(nid2[1:]))]

            if nid1[0] == "F":
                family = self._pedigree.family(int(nid1[1:]))
                for child in children:
                    if family.contains_child(child.id):
                        duplicate_child = self._pedigree.duplicate_individual(child)
                        self._branched_graph.add_node(
                            f"P{duplicate_child.id}", el=duplicate_child
                        )
                        self._branched_graph.add_edge(nid1, f"P{duplicate_child.id}")
                        self._branch_links.add((child.id, duplicate_child.id))
                        logger.debug(
                            f"Added duplicate child: {child.id}, {duplicate_child.id}"
                        )

        # Create an undirected copy of graph
        self._undirected_graph = self._graph.to_undirected()


        # Create branches
        self._branches = [
            Branch(
                id=i,
                subgraph=component,
                parent=self,
                font_size=self.font_size,
                hmargin=self.hmargin,
                node_height=self.node_height
            )
            for i, component in enumerate(
                self._branched_graph.subgraph(c).copy()
                for c in nx.weakly_connected_components(self._branched_graph)
            )
        ]

        logger.info(f"Family graph and branch creation took {time.time()-create_start:.2f}s")

    def _layout(self):
        """Calculate layout for graph"""
        logger.info(f"Starting graph layout for {len(self._branches)} branches")
        layout_start = time.time()

        branch_graph = nx.Graph()

        x = self.page_margin
        y = self.page_margin

        for i, branch in enumerate(self._branches):
            branch_layout_start = time.time()
            branch.layout()
            branch.set_coordinates(x, y)
            branch.persist_coordinates()
            bwidth, bheight = branch.size()
            x += bwidth + self.hmargin*10
            logger.debug(f"<Branch {i}> Width: {bwidth:.2f} Height: {bheight:.2f}")
            logger.debug(f"<Branch {i}> layout took: {time.time()-branch_layout_start:.4f}s")
        logger.info(f"Graph layout took: {time.time()-layout_start:.2f}s")




