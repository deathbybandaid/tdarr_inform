

from .index_html import Index_HTML
from .versions_html import Versions_HTML
from .diagnostics_html import Diagnostics_HTML
from .settings_html import Settings_HTML
from .scheduler_html import Scheduler_HTML


class Tdarr_Inform_web_Pages():

    def __init__(self, tdarr_inform):
        self.tdarr_inform = tdarr_inform

        self.index_html = Index_HTML(tdarr_inform)
        self.versions_html = Versions_HTML(tdarr_inform)
        self.diagnostics_html = Diagnostics_HTML(tdarr_inform)
        self.settings_html = Settings_HTML(tdarr_inform)
        self.scheduler_html = Scheduler_HTML(tdarr_inform)
