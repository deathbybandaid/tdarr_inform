import os


class Tdarr():

    def __init__(self, settings, logger, web):
        self.logger = logger
        self.config = settings
        self.web = web

    def inform(self, inform_dict):
        for dbID in list(inform_dict.keys()):
            self.do_tdarr_inform(dbID, inform_dict[dbID])

    def get_inform_dict(self, file_path_list):
        # Search Tdarr API for library database ID's
        # Dedupe dbID/file_path combinations
        inform_dict = {}

        # Cycle through input list and append inform_dict
        for file_path in file_path_list:
            self.logger.info("Event Item: %s" % file_path)
            self.logger.info("Searching tdarr API for item's library ID")

            # Perform search by exact path. Often expect failure especially with new files
            self.logger.info("Checking for Match by directory path: %s" % file_path)
            dbID = self.do_file_search(file_path)

            # No precise match found, search by directories starting with file's folder path and going backwards
            if not dbID:
                self.logger.warning("No exact match found, searching for library ID from Reverse Recursive Directory matching")
                dbID = self.do_reverse_recursive_directory_search(file_path)

            # Absolutely no match possible
            if not dbID:
                self.logger.error("No match found for %s" % file_path)

            # Success
            else:
                self.logger.info("Found Library ID %s" % dbID)
                if dbID not in list(inform_dict.keys()):
                    inform_dict[dbID] = []
                if file_path not in inform_dict[dbID]:
                    inform_dict[dbID].append(file_path)
                self.logger.error("Found Library ID %s" % dbID)
        return inform_dict

    def do_file_search(self, arr_file_path):
        payload = {
                    "data": {
                            "string": arr_file_path,
                            "lessThanGB": 9999,
                            "greaterThanGB": 0
                            }
                    }
        headers = {"content-type": "application/json"}
        response = self.web.post("%s/api/v2/search-db" % self.address_without_creds, json=payload, headers=headers)
        try:
            response_json = response.json()
        except Exception:
            return None
        if not len(response_json):
            return None
        dbIDs = [x["DB"] for x in response_json if "DB" in list(x.keys())]
        dbIDs = list(set(dbIDs))
        if len(dbIDs) > 1:
            return None
        return dbIDs[0]

    def do_reverse_recursive_directory_search(self, arr_file_path):
        dbID = None
        arr_dir_path = os.path.dirname(arr_file_path)
        checked_paths = []
        while self.check_path(arr_dir_path, checked_paths):
            self.logger.info("Checking for Match by directory path: %s" % arr_dir_path)
            dbID = self.do_file_search(arr_dir_path)

            # Found
            if dbID:
                break

            # Continue search
            self.logger.warn("No match found for directory path: %s" % arr_dir_path)
            checked_paths.append(arr_dir_path)
            arr_dir_path = os.path.dirname(arr_dir_path)

        return dbID

    def check_path(self, arr_dir_path, checked_paths):
        if arr_dir_path in checked_paths:
            return False
        if not self.config.dict['tdarr']["accept_root_drive_path"]:
            if arr_dir_path != os.path.abspath(os.sep):
                return True
            elif not arr_dir_path.endswith(":\\"):
                return True
            return False
        return True

    def do_tdarr_inform(self, dbID, file_paths):
        headers = {"content-type": "application/json"}
        payload = {
                    "data": {
                      "scanConfig": {
                        "dbID": dbID,
                        "arrayOrPath": file_paths,
                        "mode": "scanFolderWatcher"
                      }
                    }
                  }
        response = self.web.post("%s/api/v2/scan-files" % self.address_without_creds, json=payload, headers=headers)
        self.logger.info("Tdarr response: %s" % response.text)

    @property
    def address(self):
        return self.config.dict["tdarr"]["address"]

    @property
    def port(self):
        return self.config.dict["tdarr"]["port"]

    @property
    def proto(self):
        return "https://" if self.config.dict['tdarr']["ssl"] else "http://"

    @property
    def address_without_creds(self):
        return '%s%s:%s' % (self.proto, self.address, str(self.port))
