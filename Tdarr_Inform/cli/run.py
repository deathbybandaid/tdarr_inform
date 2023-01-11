
import sys
import pathlib
import argparse
import json

import Tdarr_Inform.exceptions
import Tdarr_Inform.config
import Tdarr_Inform.logger
import Tdarr_Inform.versions
import Tdarr_Inform.web

import Tdarr_Inform.handlers

NO_ERR_CODE = 0
ERR_CODE = 1
ERR_CODE_NO_RESTART = 2


def build_args_parser(script_dir):
    """
    Build argument parser for tdarr_inform.
    """

    if (not len(sys.argv) > 1):
        default_mode = "custom_script"
    else:
        default_mode = "manual"

    parser = argparse.ArgumentParser(description='tdarr_inform')
    parser.add_argument('-c', '--config', dest='cfg', type=str, default=pathlib.Path(script_dir).joinpath('config.ini'), required=False, help='configuration file to load.')
    parser.add_argument('--setup', dest='setup', type=str, required=False, nargs='?', const=True, default=False, help='Setup Configuration file.')
    parser.add_argument('--iliketobreakthings', dest='iliketobreakthings', type=str, nargs='?', const=True, required=False, default=False, help='Override Config Settings not meant to be overridden.')
    parser.add_argument('-v', '--version', dest='version', type=str, required=False, nargs='?', const=True, default=False, help='Show Version Number.')
    parser.add_argument('--mode', dest='mode', type=str, required=False, nargs='?', default=default_mode, help='The mode the Script will use: ENV variables, manual entry, server mode.')
    parser.add_argument('--filepath', dest='filepath', type=str, required=False, nargs='?', default=None, help='File path, to be used with --mode manual.')

    return parser.parse_args()


def get_version(script_dir):
    versions_string = ""
    version_file = pathlib.Path(script_dir).joinpath("version.json")
    with open(version_file, 'r') as jsonversion:
        core_versions = json.load(jsonversion)
    for item in list(core_versions.keys()):
        if versions_string != "":
            spaceprefix = ", "
        else:
            spaceprefix = ""
        versions_string += "%s%s %s" % (spaceprefix, item, core_versions[item])
    return versions_string


def run(args, settings, logger, script_dir, versions, web):

    valid_modes = ["custom_script", "manual"]
    if args.mode not in valid_modes:
        logger.error("Invalid mode: %s" % args.mode)
        return ERR_CODE

    logger.info("tdarr_inform called with %s mode" % args.mode)
    if args.mode == "custom_script":
        Tdarr_Inform.handlers.CustomScript(settings, logger, web)
    elif args.mode == "manual":
        Tdarr_Inform.handlers.Manual(settings, logger, web, args.filepath)

    return NO_ERR_CODE


def start(args, script_dir):
    """
    Get Configuration for tdarr_inform and start.
    """

    try:
        settings = Tdarr_Inform.config.Config(args, script_dir)
    except Tdarr_Inform.exceptions.ConfigurationError as exerror:
        sys.stderr.write(exerror)
        return ERR_CODE

    # Setup Logging
    logger = Tdarr_Inform.logger.Logger(settings)
    settings.logger = logger

    # Setup Version System
    versions = Tdarr_Inform.versions.Versions(settings, logger)

    loading_versions_string = ""
    core_versions = versions.get_core_versions()
    for item in list(core_versions.keys()):
        if loading_versions_string != "":
            spaceprefix = ", "
        else:
            spaceprefix = " "
        loading_versions_string += "%s%s %s" % (spaceprefix, core_versions[item]["name"], core_versions[item]["version"])

    logger.info("Loading %s" % loading_versions_string)

    logger.info("Importing Core config values from Configuration File: %s" % settings.config_file)

    logger.debug("Logging to File: %s" % logger.log_filepath)

    # Continue non-core settings setup
    settings.secondary_setup()

    logger.debug("Setting Up shared Web Requests system.")
    web = Tdarr_Inform.web.WebReq()

    # Continue Version System Setup
    versions.secondary_setup(web)

    return run(args, settings, logger, script_dir, versions, web)


def config_setup(args, script_dir):
    """
    Setup Config file.
    """

    settings = Tdarr_Inform.config.Config(args, script_dir)
    settings.setup_user_config()
    return NO_ERR_CODE


def main(script_dir):
    """
    tdarr_inform run script entry point.
    """

    try:
        args = build_args_parser(script_dir)

        if args.version:
            versions_string = get_version(script_dir)
            sys.stdout.write("\n%s\n" % versions_string)
            return ERR_CODE

        if args.setup:
            return config_setup(args, script_dir)

        return start(args, script_dir)

    except KeyboardInterrupt:
        sys.stdout.write("\n\nInterrupted")
        return ERR_CODE


if __name__ == '__main__':
    """
    Trigger main function.
    """
    main()
