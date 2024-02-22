#!/usr/bin/env python3
# coding=utf-8
# pylama:ignore=E402

"""
`monkey.patch_all()`` must be run as soon as possible.
Without this running right here, the webserver doesn't work well.

If this import fails, the script will restart later in case it was a missing dependency.
"""
try:
    from gevent import monkey
    monkey.patch_all()
    gevent_check = True
except ModuleNotFoundError:
    gevent_check = False

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
deps = Dependencies(SCRIPT_DIR, web=True)


"""
If gevent was unable to import at the top of `main.py`, the script will restart.
If Dependencies checks were able to install it, the script should be able to continue past this point.
If this check fails, you could get stuck looping and never reaching the actual `Tdarr_Inform_web` script.
"""
if not gevent_check:
    print("gevent was missing, restarting...")
    os.execl(sys.executable, sys.executable, *sys.argv)
    sys.exit()

"""
Import the Tdarr_Inform CLI.
"""
from Tdarr_Inform.cli import run

"""
`Tdarr_Inform_web` is part of, yet seperate from the Tdarr_Inform backend code. This gets imported while we are right here next to it.
"""
import Tdarr_Inform_web


if __name__ == "__main__":
    """Calls Tdarr_Inform.cli running methods."""
    sys.exit(run.main(SCRIPT_DIR, Tdarr_Inform_web, deps))
