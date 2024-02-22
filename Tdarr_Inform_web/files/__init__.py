

from .favicon_ico import Favicon_ICO
from .style_css import Style_CSS


class Tdarr_Inform_web_Files():

    def __init__(self, tdarr_inform):
        self.tdarr_inform = tdarr_inform

        self.favicon = Favicon_ICO(tdarr_inform)
        self.style = Style_CSS(tdarr_inform)
