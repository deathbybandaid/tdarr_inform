from Tdarr_Inform.tdarr import Tdarr


class Manual():

    def __init__(self, settings, logger, web, filepath):
        """
        Handling for script being run in env mode
        """
        self.logger = logger
        if not filepath:
            self.logger.error("No filepath given, Exiting")
            raise Exception("No filepath given, Exiting")

        self.logger.info("tdarr_inform Recieved Manual Event from CLI")

        file_path_list = self.get_file_path_list(filepath)

        tdarr = Tdarr(settings, logger, web)
        inform_dict = tdarr.get_inform_dict(file_path_list)
        if not len(inform_dict.keys()):
            self.logger.error("No matches found, Exiting")
            raise Exception("No matches found, Exiting")
        tdarr.inform(inform_dict)

    def get_file_path_list(self, filepath):
        file_paths = []

        if "," in filepath:
            file_paths.extend(filepath.split(","))
        else:
            file_paths = [filepath]

        if not len(file_paths):
            self.logger.error("No File paths retrieved from input.")
            raise Exception("No File paths retrieved from input.")

        return file_paths
