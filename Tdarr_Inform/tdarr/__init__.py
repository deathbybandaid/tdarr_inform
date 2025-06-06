import os
import uuid
from pathlib import Path, PureWindowsPath


class Tdarr():

    def __init__(self, settings, logger, web):
        self.logger = logger
        self.config = settings
        self.web = web

        self.event_uuid = str(uuid.uuid4())[:8]
        self.logger.debug("Assigning Event Item uuid: %s" % self.event_uuid)

    def inform(self, inform_dict):
        for dbID in list(inform_dict.keys()):
            self.do_tdarr_inform(dbID, inform_dict[dbID])

    def get_inform_dict(self, file_path_list):
        # Search Tdarr API for library database ID's
        # Dedupe dbID/file_path combinations
        inform_dict = {}

        # Dedupe the list
        self.logger.info("[%s] Found %s File/Directory path(s) in webhook. Running De-Duplication." % (self.event_uuid, len(file_path_list)))
        deduplicated_list = []
        for file_path in file_path_list:
            if file_path not in deduplicated_list:
                deduplicated_list.append(file_path)
        self.logger.info("[%s] Pre-Dedupe Count: %s, Deduped Count: %s" % (self.event_uuid, len(file_path_list), len(deduplicated_list)))

        # Cycle through input list and append inform_dict
        self.logger.info("[%s] Processing %s File/Directory path(s) against Tdarr API." % (self.event_uuid, len(deduplicated_list)))
        event_counter = 1

        for file_path in deduplicated_list:
            item_uuid = "%s-%s" % (self.event_uuid, event_counter)
            event_counter += 1

            self.logger.info("[%s] Event Item: %s" % (item_uuid, file_path))

            formatted_file_paths = []
            if self.path_slash_format == "unaltered":
                formatted_file_paths.append(file_path)
            elif self.path_slash_format == "both":
                self.logger.info("[%s] Config Setting will use both forward and back slashes for file paths" % (item_uuid))
                for slash_format in ["forward", "back"]:
                    formatted_file_paths.append(self.format_path_slash(file_path, slash_format))
            else:
                formatted_file_path = self.format_path_slash(file_path, self.path_slash_format)
                if file_path != formatted_file_path:
                    self.logger.info("[%s] Config Setting for %s slash rewrites to: %s" % (item_uuid, self.path_slash_format, formatted_file_path))
                formatted_file_paths.append(formatted_file_path)

            dbID = None
            for formatted_file_path in formatted_file_paths:

                # Perform search by exact path. Often expect failure especially with new files
                if not dbID:
                    self.logger.info("[%s] Checking for Exact Match by file path: %s" % (item_uuid, formatted_file_path))
                    dbID = self.do_file_search(formatted_file_path)
                if dbID:
                    self.logger.warning("[%s] Exact match found!" % (item_uuid))

            # No precise match found, search by directories starting with file's folder path and going backwards
            if not dbID:
                self.logger.warning("[%s] No exact match found, searching for library ID from Reverse Recursive Directory matching" % (item_uuid))
                dbID = self.do_reverse_recursive_directory_search(item_uuid, file_path)

            # Absolutely no match possible
            if not dbID:
                self.logger.error("[%s] No match found for %s" % (item_uuid, formatted_file_path))

            # Success
            else:
                self.logger.info("[%s] Found Library ID %s" % (item_uuid, dbID))
                if dbID not in list(inform_dict.keys()):
                    inform_dict[dbID] = []
                if formatted_file_path not in inform_dict[dbID]:
                    inform_dict[dbID].append(formatted_file_path)

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

    def do_reverse_recursive_directory_search(self, item_uuid, arr_file_path):

        dbID = None

        # Get parent directory
        arr_dir_path = os.path.dirname(arr_file_path)

        while not dbID:

            formatted_file_paths = []
            if self.path_slash_format == "unaltered":
                formatted_file_paths.append(arr_dir_path)
            elif self.path_slash_format == "both":
                self.logger.info("[%s] Config Setting will use both forward and back slashes for file paths" % (item_uuid))
                for slash_format in ["forward", "back"]:
                    formatted_file_paths.append(self.format_path_slash(arr_dir_path, slash_format))
            else:
                formatted_file_path = self.format_path_slash(arr_dir_path, self.path_slash_format)
                if arr_dir_path != formatted_file_path:
                    self.logger.info("[%s] Config Setting for %s slash rewrites to: %s" % (item_uuid, self.path_slash_format, formatted_file_path))
                formatted_file_paths.append(formatted_file_path)

            for formatted_file_path in formatted_file_paths:

                if not dbID:
                    if not self.accept_root_drive_path:
                        if self.check_root_path(formatted_file_path):
                            self.logger.info("[%s] Config setting prohibits scanning root directories. Not Checking: %s" % (item_uuid, formatted_file_path))
                            break

                    self.logger.info("[%s] Checking for Match by directory path: %s" % (item_uuid, formatted_file_path))
                    dbID = self.do_file_search(formatted_file_path)

                # Found
                if dbID:
                    break

                self.logger.warn("[%s] No match found for directory path: %s" % (item_uuid, formatted_file_path))

            # Found
            if dbID:
                break

            arr_dir_path = os.path.dirname(arr_dir_path)

        return dbID

    def check_root_path(self, arr_dir_path):
        if arr_dir_path == os.path.abspath(os.sep):
            return True
        elif arr_dir_path.endswith(":\\") or arr_dir_path.endswith(":/"):
            return True
        elif arr_dir_path.endswith(":\\") or arr_dir_path.endswith(":/"):
            return True
        elif arr_dir_path.endswith("\\") or arr_dir_path.endswith("/"):
            return True
        elif arr_dir_path.endswith(":"):
            return True
        return False

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
        self.logger.info("[%s] Sending %s path(s) to tdarr with Library ID %s." % (self.event_uuid, len(file_paths), dbID))
        response = self.web.post("%s/api/v2/scan-files" % self.address_without_creds, json=payload, headers=headers)
        self.logger.info("[%s] Tdarr response: %s" % (self.event_uuid, response.text))

    def format_path_slash(self, file_path, path_slash_format):
        """
        Windows uses a backslash character between folder names while almost every other computer uses a forward slash
        The config setting will either force backslashes, forward slashes, or not alter the request from *arr
        """

        if path_slash_format == "back":
            file_path = Path(file_path)
            file_path = PureWindowsPath(file_path)
            file_path = str(file_path).replace("/", "\\")
        elif path_slash_format == "forward":
            file_path = Path(file_path)
            file_path = str(file_path).replace("\\", "/")
        elif path_slash_format == "unaltered":
            file_path = file_path
        else:
            file_path = Path(file_path)
        return str(file_path)

    @property
    def accept_root_drive_path(self):
        return self.config.dict["tdarr"]["accept_root_drive_path"]

    @property
    def path_slash_format(self):
        return self.config.dict["tdarr"]["path_slash_format"]

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
