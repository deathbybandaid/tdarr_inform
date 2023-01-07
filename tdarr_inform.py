#!/usr/bin/python3

import os
import sys
import requests

"""Edit here"""
script_settings = {
                    "tdarr": {
                                "url": "http://CHANGEME:8265",
                                },
                    "logging": {
                                "log_file": False,
                                "log_file_path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "debug.log"),
                                "output_level": 0
                                }
                    }
"""Dont't edit below"""

expected_paths_env_variables = {
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


def loggit(logtext, force_err=False):
    if script_settings["logging"]["log_file"]:
        with open(script_settings["logging"]["log_file_path"], 'a') as logwrite:
            logwrite.write("%s\n" % logtext)
    if script_settings["logging"]["output_level"] or force_err:
        sys.stderr.write("%s\n" % logtext)
    else:
        sys.stdout.write("%s\n" % logtext)


def do_tdarr_inform(dbID, file_paths):
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
    response = requests.post("%s/api/v2/scan-files" % script_settings["tdarr"]["url"], json=payload, headers=headers)
    loggit("Tdarr response: %s" % response.text)


def do_file_search(arr_file_path):
    payload = {
                "data": {
                        "string": arr_file_path,
                        "lessThanGB": 9999,
                        "greaterThanGB": 0
                        }
                }
    headers = {"content-type": "application/json"}
    response = requests.post("%s/api/v2/search-db" % script_settings["tdarr"]["url"], json=payload, headers=headers)
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


def do_reverse_recursive_directory_search(arr_file_path):
    dbID = None
    arr_dir_path = os.path.dirname(arr_file_path)
    while arr_dir_path != os.path.abspath(os.sep) and not arr_dir_path.endswith(":\\"):
        arr_dir_path = os.path.dirname(arr_dir_path)
        dbID = do_file_search(arr_dir_path)
        if dbID:
            break
    return dbID


def get_file_path_list(arr):
    file_path_env_list = expected_paths_env_variables[arr["type"]][arr["event_type"]]

    valid_keys = [x for x in file_path_env_list if x in os.environ]
    if not len(valid_keys):
        invalid_keys = [x for x in file_path_env_list if x not in os.environ]
        if len(invalid_keys):
            for x in invalid_keys:
                loggit("%s Environment variable was missing." % x)
        sys.exit(1)

    env_paths = []
    for env_path_key in valid_keys:
        env_path = os.environ[env_path_key]
        if "|" in env_path:
            env_paths.extend(env_path.split("|"))
        else:
            env_paths.append(env_path)

    if not len(env_paths):
        loggit("No File paths retrieved fron Environment variables", True)
        sys.exit(1)

    arr["file_paths"] = env_paths

    return arr


def main():

    arr = {"type": None, "event_type": None, "file_paths": []}

    # Determine if called from Sonarr, Radarr, or Whisparr
    # Else, exit
    if "sonarr_eventtype" in os.environ:
        arr["type"] = "sonarr"
    elif "radarr_eventtype" in os.environ:
        arr["type"] = "radarr"
    elif "whisparr_eventtype" in os.environ:
        arr["type"] = "whisparr"
    else:
        loggit("Could not Detect a supported *arr", True)
        sys.exit(0)

    # What event_type was recieved
    arr["event_type"] = os.environ["%s_eventtype" % arr["type"]]
    loggit("tdarr_inform Recieved %s Event from %s" % (arr["event_type"], arr["type"]))

    # Gracefuilly exit a Test Event
    if arr["event_type"] == "Test":
        loggit("Success!")
        sys.exit(0)

    # Only support certain event types with this script
    supported_event_types = list(expected_paths_env_variables[arr["type"]].keys())
    if arr["event_type"] not in supported_event_types:
        loggit("%s %s is not a supported tdarr_inform Event." % (arr["type"], arr["event_type"]), True)
        sys.exit(1)

    # Obtain file_path list
    arr = get_file_path_list(arr)

    # Search Tdarr API for library database ID's
    # Dedupe dbID/file_path combinations
    inform_dict = {}
    for file_path in arr["file_paths"]:
        loggit("Event Item: %s" % file_path)
        loggit("Searching tdarr API for item's library ID")
        dbID = do_file_search(file_path)
        if not dbID:
            loggit("No exact match found, searching for library ID from Reverse Recursive Directory matching")
            dbID = do_reverse_recursive_directory_search(file_path)
        if not dbID:
            loggit("No match found")
        else:
            if dbID not in list(inform_dict.keys()):
                inform_dict[dbID] = []
            if file_path not in inform_dict[dbID]:
                inform_dict[dbID].append(file_path)

    if not len(inform_dict.keys()):
        loggit("No matches found, Exiting")
        sys.exit(1)

    loggit("Preparing payload to POST to tdarr API")
    for dbID in list(inform_dict.keys()):
        do_tdarr_inform(dbID, inform_dict[dbID])


if __name__ == "__main__":
    main()
