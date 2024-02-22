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
Install Dependencies at startup.
Caution, if dependencies fail to install, this will result in issues later on.
This is mainly here to install dependencies that have been added after upgrades,
and doing a manual install of dependencies prior to install is still reccomended.
This will read the requirements.txt file and attempt to install missing dependencies.
"""
from deps import Dependencies
deps = Dependencies(SCRIPT_DIR, web=False)

"""
Import the Tdarr_Inform CLI.
"""
from Tdarr_Inform.cli import run


if __name__ == "__main__":
    """Calls Tdarr_Inform.cli running methods."""
    sys.exit(run.main(SCRIPT_DIR, False, None))
