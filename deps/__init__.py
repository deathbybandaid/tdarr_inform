# pylama:ignore=W0611
import os
import sys
import pathlib
import subprocess

try:
    import pip
except ImportError:
    print("pip appears to not be installed")
    sys.exit(1)

import pkg_resources


class Dependencies():
    """
    Methods to check for missing dependencies.
    """

    def __init__(self, script_dir, web):
        self.script_dir = script_dir
        core_req_files = [pathlib.Path(script_dir).joinpath('requirements.txt')]
        if web:
            core_req_files.append(pathlib.Path(script_dir).joinpath('web-requirements.txt'))

        for reqfile in core_req_files:
            print("Checking and Installing Dependencies from %s" % reqfile)
            corereqs = self.get_requirements(reqfile)
            self.check_requirements(corereqs)

    @property
    def pipinstalled(self):
        """
        Output a dict of currently installed python modules.
        """

        packages_dict = {}
        installed_packages = pkg_resources.working_set
        sorted_packages = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
        for pypipreq in sorted_packages:

            if pypipreq and pypipreq != '':

                if "=" in pypipreq:
                    pypipreq = pypipreq.split("=")

                elif ">" in pypipreq:
                    pypipreq = pypipreq.split(">")

                elif "<" in pypipreq:
                    pypipreq = pypipreq.split("<")

                else:
                    pypipreq = [pypipreq, None]

                packages_dict[pypipreq[0]] = pypipreq[-1]

        return packages_dict

    def get_requirements(self, requirements_txt):
        """
        Reads a requirements.txt file for dependencies.
        """

        pipreqsdeps = {}
        piprequires = []

        # Check that the file is not empty
        file_size = os.stat(str(requirements_txt)).st_size
        if file_size != 0:
            piprequires = [line.rstrip('\n') for line in open(requirements_txt)]

        for pypipreq in piprequires:

            if pypipreq and pypipreq != '':

                if "=" in pypipreq:
                    pypipreq = pypipreq.split("=")

                elif ">" in pypipreq:
                    pypipreq = pypipreq.split(">")

                elif "<" in pypipreq:
                    pypipreq = pypipreq.split("<")

                else:
                    pypipreq = [pypipreq, None]

                pipreqsdeps[pypipreq[0]] = pypipreq[-1]

        return pipreqsdeps

    def check_requirements(self, reqs):
        """
        Check for, and install missing python modules dependencies.
        """

        installed = self.pipinstalled
        not_installed = [x for x in list(reqs.keys()) if x not in list(installed.keys())]

        for pipdep in not_installed:

            if pipdep and pipdep != '':

                print("%s missing. Attempting installation" % pipdep)

                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", pipdep])
                except subprocess.CalledProcessError:
                    print("%s Installation failed" % pipdep)
