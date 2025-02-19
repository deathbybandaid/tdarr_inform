
from .root_url import Root_URL

from .settings import Settings
from .logs import Logs
from .versions import Versions
from .debug import Debug_JSON
from .scheduler import Scheduler_API

from .route_list import Route_List

from .images import Images

from .events import Events


class Tdarr_Inform_web_API():

    def __init__(self, tdarr_inform):
        self.tdarr_inform = tdarr_inform

        self.root_url = Root_URL(tdarr_inform)

        self.settings = Settings(tdarr_inform)
        self.logs = Logs(tdarr_inform)
        self.versions = Versions(tdarr_inform)
        self.debug = Debug_JSON(tdarr_inform)
        self.scheduler = Scheduler_API(tdarr_inform)

        self.route_list = Route_List(tdarr_inform)

        self.images = Images(tdarr_inform)

        self.events = Events(tdarr_inform)
