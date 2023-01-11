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
    """Calls Tdarr_Inform.cli running methods."""
    sys.exit(run.main(SCRIPT_DIR))
