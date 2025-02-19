
import sys
import pathlib
import argparse
import json
import time

from Tdarr_Inform import Tdarr_Inform_OBJ
import Tdarr_Inform.exceptions
import Tdarr_Inform.config
import Tdarr_Inform.logger
import Tdarr_Inform.versions
import Tdarr_Inform.web
import Tdarr_Inform.handlers
from Tdarr_Inform.time_manager import Time_Manager

if "server" in sys.argv:
    import Tdarr_Inform.scheduler
    from Tdarr_Inform.db import Tdarr_Informdb

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


def run(args, settings, tdarr_inform_time, logger, db, script_dir, Tdarr_Inform_web, versions, web, scheduler, deps):

    valid_modes = ["custom_script", "manual", "server"]
    if args.mode not in valid_modes:
        logger.error("Invalid mode: %s" % args.mode)
        return ERR_CODE

    logger.info("tdarr_inform called with %s mode" % args.mode)
    if args.mode == "custom_script":
        Tdarr_Inform.handlers.CustomScript(settings, logger, web)
    elif args.mode == "manual":
        Tdarr_Inform.handlers.Manual(settings, logger, web, args.filepath)
    elif args.mode == "server":

        tdarr_inform = Tdarr_Inform_OBJ(settings, tdarr_inform_time, logger, db, versions, web, scheduler, deps)
        tdarr_informweb = Tdarr_Inform_web.Tdarr_Inform_web_HTTP_Server(tdarr_inform)

        versions.sched_init(tdarr_inform)

        try:

            # Start Flask Thread
            tdarr_informweb.start()

            # Run Scheduled Jobs thread
            tdarr_inform.scheduler.tdarr_inform_self_add(tdarr_inform)
            tdarr_inform.scheduler.run()

            # Perform Startup Tasks
            tdarr_inform.scheduler.startup_tasks()

            logger.info("Tdarr_Inform and Tdarr_Inform_web should now be running and accessible via the web interface at %s" % tdarr_inform.api.base)
            if settings.dict["logging"]["level"].upper() == "NOOB":
                logger.info("Set your [logging]level to INFO if you wish to see more logging output.")

            # wait forever
            restart_code = "restart"
            while tdarr_inform.threads["flask"].is_alive():
                time.sleep(1)

            if restart_code in ["restart"]:
                logger.info("Tdarr_Inform has been signaled to restart.")

            return restart_code

        except KeyboardInterrupt:
            return ERR_CODE_NO_RESTART

    return NO_ERR_CODE


def start(args, script_dir, tdarr_inform_time, Tdarr_Inform_web, deps):
    """
    Get Configuration for tdarr_inform and start.
    """

    try:
        settings = Tdarr_Inform.config.Config(args, script_dir, Tdarr_Inform_web)
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

    # add config to time manager
    tdarr_inform_time.setup(settings, logger)

    # Setup Database
    db = None
    if Tdarr_Inform_web:
        db = Tdarr_Informdb(settings, logger)

    logger.debug("Setting Up shared Web Requests system.")
    web = Tdarr_Inform.web.WebReq()

    scheduler = None
    if Tdarr_Inform_web:
        scheduler = Tdarr_Inform.scheduler.Scheduler(settings, logger, db)

    # Continue Version System Setup
    versions.secondary_setup(db, web, scheduler)

    return run(args, settings, tdarr_inform_time, logger, db, script_dir, Tdarr_Inform_web, versions, web, scheduler, deps)


def config_setup(args, script_dir, Tdarr_Inform_web):
    """
    Setup Config file.
    """

    settings = Tdarr_Inform.config.Config(args, script_dir, Tdarr_Inform_web)
    settings.setup_user_config()
    return NO_ERR_CODE


def main(script_dir, Tdarr_Inform_web, deps):
    """
    tdarr_inform run script entry point.
    """

    tdarr_inform_time = Time_Manager()

    try:
        args = build_args_parser(script_dir)

        if args.version:
            versions_string = get_version(script_dir)
            sys.stdout.write("\n%s\n" % versions_string)
            return ERR_CODE

        if args.setup:
            return config_setup(args, script_dir, Tdarr_Inform_web)

        if not Tdarr_Inform_web:
            return start(args, script_dir, tdarr_inform_time, Tdarr_Inform_web, deps)

        else:

            args.mode = "server"

            while True:

                returned_code = start(args, script_dir, tdarr_inform_time, Tdarr_Inform_web, deps)
                if returned_code not in ["restart"]:
                    return returned_code

    except KeyboardInterrupt:
        sys.stdout.write("\n\nInterrupted")
        return ERR_CODE


if __name__ == '__main__':
    """
    Trigger main function.
    """
    main()
