#!/usr/bin/env python3
# coding=utf-8
# pylama:ignore=E402

import os
import sys
import pathlib

"""
`SCRIPT_DIR` is a very important variable to set early on.
This is the directory `main.py` has been called from.
This information will be use to dynamically set other variables later, as well as some default locations.
"""
SCRIPT_DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

"""
Import the Tdarr_Inform CLI.
"""
from Tdarr_Inform.cli import run


if __name__ == "__main__":
    # TODO remove
    testdict = {
            "sonarr_eventtype": "Download",
            "sonarr_episodefile_path": "/Drivepool/Media/TV/Cartoons/Ben 10 (2016)/Season 2/Ben 10 (2016) - S02E31 - Chicken Nuggets of Wisdom.mkv"
            }
    for testkey in list(testdict.keys()):
        os.environ[testkey] = testdict[testkey]

    """Calls Tdarr_Inform.cli running methods."""
    sys.exit(run.main(SCRIPT_DIR))
