# -*- coding: utf-8 -*-
import configparser


class ODConfig(object):
    def __init__(self, iniFile):
        self.config = configparser.ConfigParser()
        self.config.read(iniFile, encoding='UTF-8')

    def ConfigSectionMap(self,section):
        d = {}
        options = self.config.options(section)
        for option in options:
            try:
                d[option] = self.config.get(section, option)
                if d[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                # print("exception on %s!" % option)
                d[option] = None
        return d 

    def reloadIniFile(self,iniFile):
        self.config.read(iniFile, encoding='UTF-8')