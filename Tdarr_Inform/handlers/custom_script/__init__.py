import os
import sys

from Tdarr_Inform.tdarr import Tdarr


class CustomScript():

    def __init__(self, settings, logger, web):
        """
        Handling for script being run in env mode
        """

        self.logger = logger

        if not self.arr:
            self.logger.error("Could not Detect a supported *arr")
            raise Exception("Could not Detect a supported *arr")

        self.logger.info("tdarr_inform Recieved %s Event from %s" % (self.event_type, self.arr))

        # Gracefuilly exit a Test Event
        if self.event_type == "Test":
            self.logger.info("Success!")
            sys.exit(0)

        if self.event_type not in self.supported_event_types:
            self.logger.error("%s %s is not a supported tdarr_inform Event." % (self.arr, self.event_type))
            raise Exception("%s %s is not a supported tdarr_inform Event." % (self.arr, self.event_type))

        file_path_list = self.get_file_path_list()

        tdarr = Tdarr(settings, logger, web)
        inform_dict = tdarr.get_inform_dict(file_path_list)
        if not len(inform_dict.keys()):
            self.logger.error("No matches found, Exiting")
            raise Exception("No matches found, Exiting")
        tdarr.inform(inform_dict)

    def get_file_path_list(self):
        env_paths = []

        valid_keys = [x for x in self.file_path_env_list if x in os.environ]
        if not len(valid_keys):
            invalid_keys = [x for x in self.file_path_env_list if x not in os.environ]
            if len(invalid_keys):
                for x in invalid_keys:
                    self.logger.error("%s Environment variable was missing." % x)
            raise Exception("No Valid Environment variables were found.")

        for env_path_key in valid_keys:
            env_path = os.environ[env_path_key]
            if "|" in env_path:
                env_paths.extend(env_path.split("|"))
            else:
                env_paths.append(env_path)

        if not len(env_paths):
            self.logger.error("No File paths retrieved from Environment variables")
            raise Exception("No File paths retrieved from Environment variables")

        return env_paths

    @property
    def supported_event_types(self):
        return list(self.expected_paths_env_variables[self.arr].keys())

    @property
    def arr(self):
        # Determine if called from Sonarr, Radarr, or Whisparr
        if "sonarr_eventtype" in os.environ:
            return "sonarr"
        elif "radarr_eventtype" in os.environ:
            return "radarr"
        elif "whisparr_eventtype" in os.environ:
            return "whisparr"
        else:
            return None

    @property
    def event_type(self):
        return os.environ["%s_eventtype" % self.arr]

    @property
    def file_path_env_list(self):
        return self.expected_paths_env_variables[self.arr][self.event_type]

    @property
    def expected_paths_env_variables(self):
        return {
                "sonarr": {
                            "Download": ["sonarr_episodefile_path", "sonarr_deletedpaths"],
                            "Rename": ["sonarr_series_path"],
                            "EpisodeFileDelete": ["sonarr_episodefile_path"],
                            "SeriesDelete": ["sonarr_series_path"]
                            },
                "radarr": {
                            "Download": ["radarr_moviefile_path", "radarr_deletedpaths"],
                            "Rename": ["radarr_moviefile_paths", "radarr_moviefile_previouspaths"],
                            "MovieFileDelete": ["radarr_moviefile_path"],
                            "MovieDelete": ["radarr_movie_path"]
                            },
                "whisparr": {
                            "Download": ["whisparr_moviefile_path", "whisparr_deletedpaths"],
                            "Rename": ["whisparr_moviefile_paths", "whisparr_moviefile_previouspaths"],
                            "MovieFileDelete": ["whisparr_moviefile_path"],
                            "MovieDelete": ["whisparr_movie_path"]
                            }
                }
