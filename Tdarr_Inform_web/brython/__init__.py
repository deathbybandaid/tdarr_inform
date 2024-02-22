

from .brython import Brython
from .brython_stdlib import Brython_stdlib

from .brython_bry import Brython_bry


class Tdarr_Inform_web_Brython():

    def __init__(self, tdarr_inform):
        self.tdarr_inform = tdarr_inform

        self.brython = Brython(tdarr_inform)
        self.brython_stdlib = Brython_stdlib(tdarr_inform)

        self.brython_bry = Brython_bry(tdarr_inform)
