import os
import configparser
import pathlib
import json

import Tdarr_Inform.exceptions
from Tdarr_Inform.tools import isint, isfloat, is_arithmetic


class Config():
    """
    Methods for maintaining the Config.
    """

    def __init__(self, args, script_dir, Tdarr_Inform_web):

        self.internal = {}
        self.conf_default = {}
        self.dict = {}
        self.config_file = args.cfg
        self.iliketobreakthings = args.iliketobreakthings

        self.conf_components = ["value", "description", "valid_options",
                                "config_file", "config_web",
                                "config_web_hidden", "required"]

        self.check_config_file()
        self.core_setup(script_dir)
        self.user_config_core()
        self.config_verification()

    def secondary_setup(self):
        """
        Perform setup post logger and setup.
        """

        self.user_config()

    def core_setup(self, script_dir):
        """
        Setup enough of the config for core functionality.
        """

        data_dir = pathlib.Path(script_dir).joinpath('data')
        Tdarr_Inform_web_dir = pathlib.Path(script_dir).joinpath('Tdarr_Inform_web')
        www_dir = pathlib.Path(Tdarr_Inform_web_dir).joinpath('www_dir')

        self.internal["paths"] = {
                                    "script_dir": script_dir,
                                    "data_dir": data_dir,
                                    "cache_dir": pathlib.Path(data_dir).joinpath('cache'),
                                    "internal_config": pathlib.Path(data_dir).joinpath('internal_config'),
                                    "Tdarr_Inform_web_dir": Tdarr_Inform_web_dir,
                                    "www_dir": www_dir,
                                    "www_templates_dir": pathlib.Path(Tdarr_Inform_web_dir).joinpath('templates'),
                                    "font": pathlib.Path(data_dir).joinpath('garamond.ttf'),
                                    }

        for conffile in os.listdir(self.internal["paths"]["internal_config"]):

            conffilepath = os.path.join(self.internal["paths"]["internal_config"], conffile)
            if str(conffilepath).endswith(".json"):
                self.read_json_config(conffilepath)

        # Web Server Conf
        self.read_json_config(pathlib.Path(self.internal["paths"]["Tdarr_Inform_web_dir"]).joinpath("web_ui_conf.json"))

    def user_config_core(self):
        """
        Setup Core Configuration for User config file.
        """

        config_handler = configparser.ConfigParser()
        config_handler.read(self.config_file)
        for each_section in config_handler.sections():

            if each_section.lower() in list(self.dict.keys()):

                for (each_key, each_val) in config_handler.items(each_section):

                    each_val = self.get_real_conf_value(each_key, each_val)
                    import_val = True
                    if each_section in list(self.conf_default.keys()):

                        if each_key in list(self.conf_default[each_section].keys()):

                            if not self.conf_default[each_section][each_key]["config_file"] and not self.iliketobreakthings:
                                import_val = False

                    if import_val:
                        self.dict[each_section.lower()][each_key.lower()] = each_val

    def user_config(self):
        """
        Read User Configuration file.
        """

        self.read_ini_config(self.config_file)

    def setup_user_config(self):
        """
        Setup User Config File.
        """

        config_handler = configparser.ConfigParser()
        if not os.path.isfile(self.config_file):

            with open(self.config_file, 'w') as config_file:
                config_handler.write(config_file)

        current_conf = {}

        config_handler.read(self.config_file)
        for each_section in config_handler.sections():

            if each_section.lower() not in list(current_conf.keys()):
                current_conf[each_section.lower()] = {}

            for (each_key, each_val) in config_handler.items(each_section):
                each_val = self.get_real_conf_value(each_key, each_val)

                import_val = True
                if each_section in list(self.conf_default.keys()):

                    if each_key in list(self.conf_default[each_section].keys()):

                        if not self.conf_default[each_section][each_key]["config_file"] and not self.iliketobreakthings:
                            import_val = False

                if import_val:
                    current_conf[each_section.lower()][each_key.lower()] = each_val

        for config_section in list(self.conf_default.keys()):

            if config_section not in list(current_conf.keys()):
                current_conf[config_section] = {}

            for config_item in list(self.conf_default[config_section].keys()):

                writeval = True
                if config_item in list(current_conf[config_section].keys()):
                    writeval = False

                if writeval:
                    value = self.conf_default[config_section][config_item]["value"]
                    self.write(config_item, value, config_section)

    def check_required_missing(self):
        """
        Check for missing Configuration Options.
        """

        required_missing = {}

        # create dict and combine items
        for config_section in list(self.conf_default.keys()):

            for config_item in list(self.conf_default[config_section].keys()):

                if self.conf_default[config_section][config_item]["required"]:

                    if not self.dict[config_section][config_item]:

                        if config_section not in list(required_missing.keys()):
                            required_missing[config_section] = []

                        required_missing[config_section].append(config_item)

        for config_section in list(required_missing.keys()):
            self.logger.info("Required configuration options missing: [%s]%s" % (config_section, ", ".join(required_missing[config_section])))

    def config_verification(self):
        """
        Verify required config system is ready.
        """

        if self.dict["main"]["cache_dir"]:

            if not pathlib.Path(self.dict["main"]["cache_dir"]).is_dir():
                raise Tdarr_Inform.exceptions.ConfigurationError("Invalid Cache Directory. Exiting...")

            self.internal["paths"]["cache_dir"] = pathlib.Path(self.dict["main"]["cache_dir"])

        cache_dir = self.internal["paths"]["cache_dir"]

        logs_dir = pathlib.Path(cache_dir).joinpath('logs')
        self.internal["paths"]["logs_dir"] = logs_dir
        if not logs_dir.is_dir():
            logs_dir.mkdir()

        self.dict["database"]["path"] = pathlib.Path(cache_dir).joinpath('tdarr_inform.db')

    def check_config_file(self):
        """
        Check for config file.
        """

        if not os.path.isfile(self.config_file):

            config_handler = configparser.ConfigParser()
            with open(self.config_file, 'w') as config_file:
                config_handler.write(config_file)

    def get_real_conf_value(self, key, confvalue):
        """
        Check config value is prepped correctly.
        """

        if not confvalue:
            confvalue = None

        elif isinstance(confvalue, type(None)):
            confvalue = None

        elif key == "xmltv_offset":
            confvalue = str(confvalue)

        elif str(confvalue) in [0, "0"]:
            confvalue = 0

        elif isint(confvalue):
            confvalue = int(confvalue)

        elif isfloat(confvalue):
            confvalue = float(confvalue)

        elif is_arithmetic(confvalue):
            confvalue = eval(confvalue)

        elif "," in confvalue:
            confvalue = confvalue.split(",")

        elif str(confvalue).lower() in ["none", ""]:
            confvalue = None

        elif str(confvalue).lower() in ["false"]:
            confvalue = False

        elif str(confvalue).lower() in ["true"]:
            confvalue = True

        return confvalue

    def read_json_config(self, conffilepath):
        """
        Read an internal config file.
        """

        with open(conffilepath, 'r') as jsonconf:
            confimport = json.load(jsonconf)

        for section in list(confimport.keys()):

            if section not in self.dict.keys():
                self.dict[section] = {}

            if section not in self.conf_default.keys():
                self.conf_default[section] = {}

            for key in list(confimport[section].keys()):

                if key not in list(self.conf_default[section].keys()):
                    self.conf_default[section][key] = {}

                confvalue = self.get_real_conf_value(key, confimport[section][key]["value"])

                self.dict[section][key] = confvalue

                self.conf_default[section][key]["value"] = confvalue

                for config_option in ["config_web_hidden", "config_file", "config_web", "required"]:

                    if config_option not in list(confimport[section][key].keys()):
                        config_option_value = False

                    else:

                        config_option_value = confimport[section][key][config_option]
                        if str(config_option_value).lower() in ["none"]:
                            config_option_value = None

                        elif str(config_option_value).lower() in ["false"]:
                            config_option_value = False

                        elif str(config_option_value).lower() in ["true"]:
                            config_option_value = True

                    self.conf_default[section][key][config_option] = config_option_value

                if "valid_options" not in list(confimport[section][key].keys()):
                    config_option_value = None

                else:

                    config_option_value = confimport[section][key]["valid_options"]

                    if "," in config_option_value:
                        config_option_value = config_option_value.split(",")

                    elif config_option_value in ["list"]:
                        config_option_value = config_option_value

                    elif config_option_value in ["integer", "int"]:
                        config_option_value = config_option_value

                    elif config_option_value in ["string", "str"]:
                        config_option_value = config_option_value

                    elif config_option_value in ["bool"]:
                        config_option_value = config_option_value

                    elif config_option_value in ["path"]:
                        config_option_value = config_option_value

                    else:
                        config_option_value = [config_option_value]

                self.conf_default[section][key]["valid_options"] = config_option_value

                if "description" not in list(confimport[section][key].keys()):
                    config_option_value = None

                else:
                    config_option_value = confimport[section][key]["description"]

                self.conf_default[section][key]["description"] = config_option_value

    def read_ini_config(self, conffilepath):
        """
        Read a user ini config file.
        """

        config_handler = configparser.ConfigParser()
        config_handler.read(conffilepath)
        for each_section in config_handler.sections():

            if each_section.lower() not in list(self.dict.keys()):
                self.dict[each_section.lower()] = {}

            for (each_key, each_val) in config_handler.items(each_section):
                each_val = self.get_real_conf_value(each_key, each_val)

                import_val = True
                if each_section in list(self.conf_default.keys()):

                    if each_key in list(self.conf_default[each_section].keys()):

                        if not self.conf_default[each_section][each_key]["config_file"] or self.iliketobreakthings:
                            import_val = False

                if import_val:
                    self.dict[each_section.lower()][each_key.lower()] = each_val

    def write(self, key, value, section):
        """
        Write changes to user config file.
        """

        if not value:
            value = None

        elif key == "xmltv_offset":
            value = str(value)

        elif str(value) in ["0"]:
            value = 0

        elif isint(value):
            value = int(value)

        elif isfloat(value):
            value = float(value)

        elif is_arithmetic(value):
            value = eval(value)

        elif isinstance(value, list):
            ",".join(value)

        elif str(value).lower() in ["none", ""]:
            value = None

        elif str(value).lower() in ["false"]:
            value = False

        elif str(value).lower() in ["true"]:
            value = True

        self.dict[section][key] = value

        config_handler = configparser.ConfigParser()
        config_handler.read(self.config_file)

        if not config_handler.has_section(section):
            config_handler.add_section(section)

        config_handler.set(section, key, str(value))

        with open(self.config_file, 'w') as config_file:
            config_handler.write(config_file)

    def __getattr__(self, name):
        """
        Quick and dirty shortcuts. Will only get called for undefined attributes.
        """

        if name in list(self.dict.keys()):
            return self.dict[name]
