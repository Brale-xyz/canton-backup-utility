"""Module providing class representing command line arguments"""

import argparse


class UtilityArgs:
    """Class to hold command line arguments"""

    def __init__(self, network, cmd):
        """
        Args:
            network (str): The Canton network to target.
            cmd (str): The command to run.
        """
        self._network = network
        self._command = cmd

    @property
    def network(self):
        return self._network

    @property
    def command(self):
        return self._command

    @staticmethod
    def get_cmd_args():
        """Static method to parse command line arguments"""
        parser = argparse.ArgumentParser(
            prog="Canton User Backup Utility",
            description="Backs up and restores user/party mappings",
        )
        parser.add_argument(
            "-n",
            "--network",
            choices=["devnet", "testnet", "mainnet"],
            help="Network to use",
        )
        parser.add_argument(
            "-c",
            "--command",
            choices=["backup_users", "restore_users"],
            help="command to run",
        )
        args = parser.parse_args()
        return UtilityArgs(args.network, args.command)
