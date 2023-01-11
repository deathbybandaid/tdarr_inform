import os
import sys
import platform
import pathlib
import json
import re


class Versions():
    """
    Tdarr_Inform versioning management system.
    """

    def __init__(self, settings, logger):
        self.config = settings
        self.logger = logger

        self.github_tdarr_inform_core_info_url = "https://raw.githubusercontent.com/deathbybandaid/tdarr_inform/main/version.json"

        self.dict = {}

        self.register_tdarr_inform()

        self.register_env()

    def secondary_setup(self, web):
        self.web = web

        self.core_versions = {}

    def get_online_versions(self):
        """
        Update Onling versions listing.
        """

        self.logger.debug("Checking for Online Core Versioning Information")
        core_versions = {}

        try:
            core_json = self.web.session.get(self.github_tdarr_inform_core_info_url).json()
        except self.web.exceptions.ReadTimeout as exerror:
            error_out = self.tdarr_inform.logger.lazy_exception(exerror, "Online Core Versioning Information Check Failed")
            self.tdarr_inform.logger.error(error_out)
            core_json = None

        if core_json:
            for key in list(core_json.keys()):
                core_versions[key] = {"name": key, "version": core_json[key], "type": "core"}
            self.core_versions = core_versions

    def get_core_versions(self):
        returndict = {}
        for item in list(self.dict.keys()):
            if self.dict[item]["type"] == "Tdarr_Inform":
                returndict[item] = self.dict[item].copy()
        return returndict

    def register_version(self, item_name, item_version, item_type):
        """
        Register a version item.
        """

        self.logger.debug("Registering %s item: %s %s" % (item_type, item_name, item_version))
        self.dict[item_name] = {
                                "name": item_name,
                                "version": item_version,
                                "type": item_type
                                }

    def register_tdarr_inform(self):
        """
        Register core version items.
        """

        script_dir = self.config.internal["paths"]["script_dir"]
        version_file = pathlib.Path(script_dir).joinpath("version.json")
        with open(version_file, 'r') as jsonversion:
            versions = json.load(jsonversion)

        for key in list(versions.keys()):
            self.register_version(key, versions[key], "Tdarr_Inform")

    def is_docker(self):
        path = "/proc/self/cgroup"
        if not os.path.isfile(path):
            return False
        with open(path) as f:
            for line in f:
                if re.match("\d+:[\w=]+:/docker(-[ce]e)?/\w+", line):
                    return True
            return False

    def is_virtualenv(self):
        # return True if started from within a virtualenv or venv
        base_prefix = getattr(sys, "base_prefix", None)
        # real_prefix will return None if not in a virtualenv enviroment or the default python path
        real_prefix = getattr(sys, "real_prefix", None) or sys.prefix
        return base_prefix != real_prefix

    def register_env(self):
        """
        Register env version items.
        """

        self.register_version("Python", sys.version, "env")
        if sys.version_info.major == 2 or sys.version_info < (3, 7):
            self.logger.error('Error: Tdarr_Inform requires python 3.7+. Do NOT expect support for older versions of python.')

        opersystem = platform.system()
        self.register_version("Operating System", opersystem, "env")

        system_alias = platform.release()
        self.register_version("OS Release", system_alias, "env")

        if opersystem in ["Linux", "Darwin"]:

            # Linux/Mac
            if os.getuid() == 0 or os.geteuid() == 0:
                self.logger.warning('Do not run Tdarr_Inform with root privileges.')

        elif opersystem in ["Windows"]:

            # Windows
            if os.environ.get("USERNAME") == "Administrator":
                self.logger.warning('Do not run Tdarr_Inform as Administrator.')

        else:
            # ['Java']
            if not len(opersystem):
                os_string = "."
            else:
                os_string = ": %s" % opersystem
            self.logger.warning("Uncommon Operating System, use at your own risk%s" % os_string)

        cpu_type = platform.machine()
        self.register_version("CPU Type", cpu_type, "env")

        isvirtualenv = self.is_virtualenv()
        self.register_version("Virtualenv", isvirtualenv, "env")

        isdocker = self.is_docker()
        self.register_version("Docker", isdocker, "env")
