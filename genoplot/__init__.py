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
import networkx as nx

from .genoplot import GenoPlot

__version__ = "0.0.1"

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


def main():
    pstart = time.time()
    # p = GenoPlot("sample", "sample.ged")
    # p.create_graph()
    # g = p.create_grandalf()
    p.draw()

    logger.info(f"Total time to build GenoPlot: {time.time() - pstart:.2f}s")
    logger.info(f"Total time to process: {time.time() - pstart:.2f}s")

    return p


# Test code
# import genoplot; import networkx as nx; p = genoplot.main()
