"""Module provides the Configuration class for the Backup utility"""

import os
import tomllib

from dotenv import load_dotenv
from munch import DefaultMunch, munchify

load_dotenv()


class UtilityConfig:
    """Class to hold configuration values for the Backup utility"""

    def __init__(self, network, cfg):
        network_cfg = cfg["networks"][network]
        self._config = munchify({**cfg["general"], **network_cfg}, DefaultMunch)
        self._base_url = os.getenv("BASE_URL")
        self._auth_url = os.getenv("AUTH_URL")
        self._client_id = os.getenv("CLIENT_ID") or cfg.client_id
        self._client_secret = os.getenv("CLIENT_SECRET")
        self._log_level = os.getenv("LOG_LEVEL")

    @property
    def config(self):
        return self._config

    @property
    def client_id(self):
        return self._client_id

    @property
    def client_secret(self):
        return self._client_secret

    @property
    def network(self):
        return self._config.network

    @property
    def stage(self):
        return self._config.stage

    @property
    def base_url(self):
        return self._base_url or self._config.base_url

    @property
    def auth_url(self):
        return self._auth_url or self._config.auth_url

    @property
    def backup_file(self):
        return self._config.backup_file

    @property
    def log_level(self):
        return self._log_level or self._config.log_level or "INFO"

    def to_dict(self):
        return self._config

    @staticmethod
    def from_dict(network, config_dict):
        return UtilityConfig(network, config_dict)

    @staticmethod
    def from_file(network, config_file="config.toml"):
        """Parse a TOML config file and config object"""
        with open(config_file, "rb") as f:
            cfg = tomllib.load(f)
        return UtilityConfig(network, cfg)
