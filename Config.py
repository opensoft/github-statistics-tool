"""
This is a config data loader for git-cloner utility

@author: Mikhail Dyakonov
@contact: mikhail.dyakonov@opensoftdev.com
@organization: Opensoft
"""

import json
from jsmin import jsmin
import logging
import os.path

from DictMerge import merge


class Config(object):
    """
    Reads and parses config data and returns it on demand
    """

    def __init__(self, config_file_path):
        self._config = dict()
        self.__loaded_files = set()
        self.__load_conf_file(config_file_path)
        self.__temp_folder = None


    def __getitem__(self, item):
        return self._config[item]

    def get_organisations_list(self):
        return self._config["github"]["organisations"]

    def get_timeouts(self):
        return self._config["timeouts"]

    def get_log_level(self):
        lvl = self._config["log_level"]
        if not lvl:
            return 0
        elif lvl.isdigit():
            return int(lvl)
        else:
            return logging.getLevelName(lvl)

    def __load_conf_file(self, conf_file_path, depth = 1):
        """
        Loads config files recursively (with include statement)
        :param conf_file_path:
        :param depth:
        :return:
        """
        if depth > 10:
            raise Exception("Include tree depth has exceed 10")

        if os.path.isabs(conf_file_path):
            path = conf_file_path
        else:
            path = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + conf_file_path

        if path in self.__loaded_files:
            # file has been loaded already
            logging.info("Config file %s has been loaded already, skipping it..." % path)
            return
        else:
            self.__loaded_files.add(path)

        logging.debug("Loading config file %s", path)
        try:
            with open(path) as config_file:
                mjs = jsmin(config_file.read())
                new_conf = json.loads(mjs)
                #self._config.update(new_conf)
                self._config = merge(new_conf, self._config)
        except Exception:
            raise Exception("Error in loading config file: %s" % path)

        # process includes
        if new_conf and "include" in new_conf.keys():
            for inc_file in new_conf["include"]:
                self.__load_conf_file(inc_file, depth + 1)

