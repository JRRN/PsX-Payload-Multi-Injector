import configparser
import logging
import os


logger = logging.getLogger(__name__)


class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        logger.debug("ConfigManager init path=%s", config_path)
        self._load()

    def _load(self):
        if os.path.exists(self.config_path):
            logger.debug("Loading config from %s", self.config_path)
            self.config.read(self.config_path)
        else:
            logger.info("Config not found at %s, creating defaults", self.config_path)
            self.config["DEFAULT"] = {"ip": "", "language": "es-es"}
            self._save()

    def get_ip(self):
        ip = self.config["DEFAULT"].get("ip", "192.168.1.100")
        logger.debug("Config get_ip=%s", ip)
        return ip

    def set_ip(self, ip):
        logger.debug("Config set_ip=%s", ip)
        self.config["DEFAULT"]["ip"] = ip
        self._save()

    def get_language(self):
        lang = self.config["DEFAULT"].get("language", "es-es")
        logger.debug("Config get_language=%s", lang)
        return lang

    def set_language(self, language):
        logger.debug("Config set_language=%s", language)
        self.config["DEFAULT"]["language"] = language
        self._save()

    def _save(self):
        logger.debug("Saving config to %s", self.config_path)
        with open(self.config_path, "w") as file_obj:
            self.config.write(file_obj)
