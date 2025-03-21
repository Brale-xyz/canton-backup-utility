"""Module provides the primary class for the Backup Utility"""

#! /usr/bin/env python3

import cmd
import logging
from pathlib import Path
from string import Template

import requests
import simplejson as json

from utility import cmd_args, config

# from utility.args import UtilityArgs
# from utility.config import UtilityConfig

AVAILABLE_NETWORKS = ["devnet", "testnet", "mainnet"]


class BackupUtility(cmd.Cmd):
    """Canton User Backup Utility"""

    prompt = "Backup Users> "
    intro = 'Canton User Backup Utility\nType "help" or "?"to list commands.'

    def __init__(self):
        super().__init__()
        args = cmd_args.UtilityArgs.get_cmd_args()
        self._cfg = None
        self._network = args.network
        self._token = None
        self._client_secret = None
        self._logger = None
        self.cmdqueue = [args.command, "exit"] if args.command else []

    @property
    def _base_url(self):
        return self._render_string(self._cfg.base_url)

    @property
    def _auth_url(self):
        return self._render_string(self._cfg.auth_url)

    @property
    def _list_users_uri(self):
        return f"{self._base_url}/users"

    @property
    def _list_user_rights_uri(self):
        return f"{self._base_url}/user/rights"

    @property
    def _create_user_uri(self):
        return f"{self._base_url}/user/create"

    @property
    def _client_id(self):
        return self._cfg.client_id

    @property
    def stage(self):
        return self._cfg.stage or self.network

    @property
    def network(self):
        return self._network

    def logger(self):
        """Returns a configured logger"""
        if self._logger is None:
            try:
                logging.basicConfig(
                    level=self._cfg.log_level,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            except ValueError:
                print(f"Invalid log level: {self._cfg.log_level}; defaulting to INFO")
                logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(message)s")
            self._logger = logging.getLogger(__name__)
        return self._logger

    def _get_credentials(self):
        print("Client credentials can be retrieved from Keycloak.")
        print("Please enter your client credentials:")
        self._client_secret = input(f"{self._client_id} Client Secret: ").strip()

    def _auth(self):
        if self._client_secret is None:
            self._get_credentials()
        self.logger().info("Authenticating...")
        r = requests.post(
            self._auth_url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            timeout=10,
        )
        if r.status_code == 200:
            self._token = r.json()["access_token"]
        else:
            self._client_secret = None
            self.logger().error(
                "Failed to get auth token: %s. Please reauthenticate.", r.status_code
            )

    def _perform_request(self, method, url, data=None):
        if self._token is None:
            self._auth()

        r = requests.request(
            method,
            url,
            headers={"Authorization": f"Bearer {self._token}"},
            json=data,
            timeout=10,
        )
        r.raise_for_status()
        self.logger().debug("%s: %s", method, r.status_code)
        try:
            return r.json()["result"]
        except KeyError:
            return r.json()

    def _get_users(self):
        result = self._perform_request("GET", self._list_users_uri)
        print("retrieved active users from participant")
        self.logger().debug("retrieved %s users: %s", len(result), result)
        return result

    def _list_user_rights(self, user_id):
        result = self._perform_request("POST", self._list_user_rights_uri, data={"userId": user_id})
        self.logger().debug("retrieved rights for user %s: %s", user_id, result)
        return result

    def _build_user_requests(self, users):
        user_requests = []
        for user in users:
            user["rights"] = self._list_user_rights(user["userId"])
            user_requests.append(user)
        self.logger().info("built requests for %s users", len(user_requests))
        self.logger().debug("user requests: %s", user_requests)
        return user_requests

    def _save(self, filename, data):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def _default_filename(self):
        return f"{self.stage}-{self.network}-users.json"

    def _choose_filename(self):
        print("Please select a filename:")
        return (
            input(f"Backup Filename [default: {self._default_filename()}]: ").strip()
            or self._default_filename()
        )

    def _render_string(self, template_str):
        tmpl = Template(template_str)
        return tmpl.substitute(network=self.network, stage=self.stage)

    def _backup_filename(self):
        if self._cfg.backup_file:
            return self._render_string(self._cfg.backup_file)
        return self._default_filename()

    def get_backup_file(self):
        """Gets the configured backup filename or prompts the user for a filename"""
        if self._cfg.backup_file:
            return self._backup_filename()
        return self._choose_filename()

    def _load_backup(self):
        filename = self.get_backup_file()
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.loads(f.read())
        except FileNotFoundError:
            self.logger().error("Backup file not found")
            return None

    def _save_json_data(self, filename, data):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def _save_backup(self, user_requests):
        filename = self.get_backup_file()
        if Path(filename).is_file() and self._preserve_existing_file(filename):
            return self._save_backup(user_requests)
        return self._save_json_data(filename, user_requests)

    def _preserve_existing_file(self, filename):
        if self._cfg.backup_file:
            return False
        print(f"Backup file {filename} already exists")
        if input("Overwrite? (y/n): ").strip().lower() == "y":
            return False
        return True

    def _create_user(self, create_req):
        try:
            print(f"Creating user: {create_req['userId']}")
            return self._perform_request("POST", self._create_user_uri, create_req)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:
                return {"error": f"User {create_req['userId']} already exists"}
            return {"error": e.response.text}

    def preloop(self):
        if self._network is None:
            print("Please select a network:")
            print("Available Networks: devnet, testnet, mainnet")

        while self._network is None:
            try:
                selection = input("Network: ").strip().lower()
                self._network = {net: net for net in AVAILABLE_NETWORKS}[selection]
            except KeyError:
                print("Invalid Network, network must be devnet, testnet, or mainnet")
                self.network = None
        self._cfg = config.UtilityConfig.from_file(self.network)
        self._client_secret = self._cfg.client_secret

    # pylint: disable-next=W0613
    def do_reauth(self, arg):
        """command loop command to reauthenticate to the Validator API"""
        self._token = None
        self._auth()

    # pylint: disable-next=W0613
    def do_backup_users(self, arg):
        """command loop command to backup users"""
        users = self._get_users()
        user_requests = self._build_user_requests(users)
        self._save_backup(user_requests)

    # pylint: disable-next=W0613
    def do_restore_users(self, arg):
        """command loop command to restore users"""
        user_requests = self._load_backup()
        if user_requests is not None:
            results = {"success": [], "failed": []}
            for user_request in user_requests:
                r = self._create_user(user_request)
                self.logger().debug("created user %s: %s", user_request["userId"], r)
                try:
                    results["failed"].append(r["error"])
                except KeyError:
                    results["succeeded"].append(user_request["userId"])
            print("\nRestore user results:")
            print(json.dumps(results, indent=2))

    # pylint: disable-next=W0613
    def do_exit(self, arg):
        "command loop command to exit"
        return True

    def configure(self, configuration: config.UtilityConfig):
        self._cfg = configuration
