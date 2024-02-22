# coding=utf-8

from .api import Tdarr_Inform_API_URLs

from Tdarr_Inform.tools import checkattr


class Tdarr_Inform_INT_OBJ():

    def __init__(self, ext_tdarr_inform, settings, tdarr_inform_time, logger, db, versions, web, scheduler, deps):
        """
        An internal catalogue of core methods.
        """

        self.ext_tdarr_inform = ext_tdarr_inform

        self.versions = versions
        self.version = versions.dict["Tdarr_Inform"]["version"]
        self.config = settings
        self.logger = logger
        self.db = db
        self.web = web
        self.scheduler = scheduler
        self.deps = deps
        self.time = tdarr_inform_time

        self.api = Tdarr_Inform_API_URLs(settings, self.web, versions, logger)

        self.threads = {}

    def __getattr__(self, name):
        """
        Quick and dirty shortcuts. Will only get called for undefined attributes.
        """

        if checkattr(self.ext_tdarr_inform, name):
            return eval("self.ext_tdarr_inform.%s" % name)


class Tdarr_Inform_OBJ():

    def __init__(self, settings, tdarr_inform_time, logger, db, versions, web, scheduler, deps):
        """
        The Core Backend.
        """

        logger.info("Initializing Tdarr_Inform Core Functions.")
        self.tdarr_inform = Tdarr_Inform_INT_OBJ(self, settings, tdarr_inform_time, logger, db, versions, web, scheduler, deps)

    def __getattr__(self, name):
        """
        Quick and dirty shortcuts. Will only get called for undefined attributes.
        """

        if checkattr(self.tdarr_inform, name):
            return eval("self.tdarr_inform.%s" % name)

        elif checkattr(self.tdarr_inform.device, name):
            return eval("self.tdarr_inform.device.%s" % name)
