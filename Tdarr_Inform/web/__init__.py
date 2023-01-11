import requests

from Tdarr_Inform.tools import checkattr


class WebReq():
    """
    The sessions manager for Tdarr_Inform.
    """

    def __init__(self):
        self.session = requests.Session()
        self.exceptions = requests.exceptions

    def __getattr__(self, name):
        """
        Quick and dirty shortcuts. Will only get called for undefined attributes.
        """

        if checkattr(self.session, name):
            return eval("self.session.%s" % name)
