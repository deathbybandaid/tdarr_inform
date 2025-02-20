
from Tdarr_Inform.tools import checkattr
from Tdarr_Inform.tdarr import Tdarr


class Webhook_Event():

    def __init__(self, tdarr_inform, webhook_json, process_event):
        """
        Handling for script being run in env mode
        """

        self.tdarr_inform = tdarr_inform

        self.webhook_json = webhook_json

        if not self.arr:
            self.tdarr_inform.logger.error("Could not Detect a supported *arr")
            raise Exception("Could not Detect a supported *arr")

        self.tdarr_inform.logger.info("tdarr_inform Recieved %s Event from %s" % (self.event_type, self.arr))

        # Gracefuilly exit a Test Event
        if self.event_type == "Test":
            self.tdarr_inform.logger.info("Test Success!")
            return

        if self.event_type not in self.valid_event_types:
            self.tdarr_inform.logger.error("%s %s is not a supported tdarr_inform Event." % (self.arr, self.event_type))
            raise Exception("%s %s is not a supported tdarr_inform Event." % (self.arr, self.event_type))

        if process_event:
            self.process_information()

    def process_information(self):
        file_path_list = self.get_file_path_list()

        tdarr = Tdarr(self.tdarr_inform.config, self.tdarr_inform.logger, self.tdarr_inform.web)
        inform_dict = tdarr.get_inform_dict(file_path_list)
        if not len(inform_dict.keys()):
            self.tdarr_inform.logger.error("No matches found, Exiting")
            raise Exception("No matches found, Exiting")
        tdarr.inform(inform_dict)

    def get_file_path_list(self):
        webhook_file_paths = []

        files_entries = [x for x in list(self.expected_webhook_info_base[self.arr][self.event_type].keys()) if x in list(self.webhook_json.keys())]
        for file_entry in files_entries:
            file_entry_path_list = self.webhook_json[file_entry]
            if not isinstance(file_entry_path_list, list):
                file_entry_path_list = [file_entry_path_list]
            for file_entry_path in file_entry_path_list:
                actual_path_keys = [x for x in self.expected_webhook_info_base[self.arr][self.event_type][file_entry] if x in list(file_entry_path.keys())]
                for path_key in actual_path_keys:
                    path_append = file_entry_path[path_key]
                    webhook_file_paths.append(path_append)

        if not len(webhook_file_paths):
            self.tdarr_inform.logger.warn("No File paths extracted from expected keys from Webhook Event, checking fallback keys.")
            fallback_keys = [x for x in list(self.expected_webhook_info_base[self.arr]["fallback"].keys()) if x in list(self.webhook_json.keys())]
            for file_entry in fallback_keys:
                file_entry_path_list = self.webhook_json[file_entry]
                if not isinstance(file_entry_path_list, list):
                    file_entry_path_list = [file_entry_path_list]
                for file_entry_path in file_entry_path_list:
                    actual_path_keys = [x for x in self.expected_webhook_info_base[self.arr][self.event_type][file_entry] if x in list(file_entry_path.keys())]
                    for path_key in actual_path_keys:
                        path_append = file_entry_path[path_key]
                        webhook_file_paths.append(path_append)

        if not len(webhook_file_paths):
            self.tdarr_inform.logger.error("No File paths retrieved from Webhook Event")
            raise Exception("No File paths retrieved from Webhook Event")

        return webhook_file_paths

    @property
    def arr(self):
        # Determine if called from Sonarr, Radarr, or Whisparr
        if "instanceName" in list(self.webhook_json.keys()):
            instanceName = self.webhook_json["instanceName"]
            if instanceName in self.valid_arrs:
                return instanceName
        # NOTE: Whisparr also uses "series" even though event types are OnMovieAdded
        elif "series" in list(self.webhook_json.keys()):
            return "Sonarr"
        elif "movie" in list(self.webhook_json.keys()):
            return "Radarr"
        return None

    @property
    def event_type(self):
        if "eventType" in list(self.webhook_json.keys()):
            return self.webhook_json["eventType"]
        return None

    @property
    def valid_arrs(self):
        return list(self.expected_webhook_info_base.keys())

    @property
    def valid_event_types(self):
        return list(self.expected_webhook_info_base[self.arr].keys())

    @property
    def expected_webhook_info_base(self):
        return {
            "Sonarr": {
                "Download": {
                    "episodeFile": ["path"],
                    "deletedFiles": ["path"]
                    },
                "Upgrade": {
                    "episodeFile": ["path"],
                    "deletedFiles": ["path"]
                    },
                "Rename": {
                    "renamedEpisodeFiles": ["path", "previousPath"]
                    },
                "SeriesDelete": {
                    "episodeFile": ["path"]
                    },
                "EpisodeFileDelete": {
                    "episodeFile": ["path"]
                    },
                "EpisodeFileDeleteForUpgrade": {
                    "episodeFile": ["path"],
                    "deletedFiles": ["path"]
                    },
                "fallback": {
                    "series": ["path"]
                    }
            },
            "Radarr": {
                "Download": {
                    "movieFile": ["path"],
                    "deletedFiles": ["path"]
                    },
                "Upgrade": {
                    "movieFile": ["path"],
                    "deletedFiles": ["path"]
                    },
                "Rename": {
                    "renamedMovieFiles": ["path", "previousPath"]
                    },
                "MovieDelete": {
                    "movieFile": ["path"]
                    },
                "MovieFileDelete": {
                    "movieFile": ["path"],
                    "deletedFiles": ["path"]
                    },
                "MovieFileDeleteForUpgrade": {
                    "movieFile": ["path"],
                    "deletedFiles": ["path"]
                    },
                "fallback": {
                    "movie": ["folderPath"]
                    }
            },
            "Whisparr": {
                "Download": {
                    "movieFile": ["path"],
                    "deletedFiles": ["path"]
                    },
                "Upgrade": {
                    "movieFile": ["path"],
                    "deletedFiles": ["path"]
                    },
                "Rename": {
                    "renamedMovieFiles": ["path", "previousPath"]
                    },
                "MovieDelete": {
                    "movieFile": ["path"]
                    },
                "MovieFileDelete": {
                    "movieFile": ["path"],
                    "deletedFiles": ["path"]
                    },
                "MovieFileDeleteForUpgrade": {
                    "movieFile": ["path"],
                    "deletedFiles": ["path"]
                    },
                "fallback": {
                    "movie": ["folderPath"]
                    }
            },
        }

    def __getattr__(self, name):
        """
        Quick and dirty shortcuts. Will only get called for undefined attributes.
        """

        if checkattr(self.tdarr_inform, name):
            return eval("self.tdarr_inform.%s" % name)
