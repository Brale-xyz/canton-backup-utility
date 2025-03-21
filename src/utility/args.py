import argparse


class UtilityArgs:
    def __init__(self, network, cmd):
        self.network = network
        self.command = cmd
    
    @staticmethod
    def get_cmd_args():
        parser = argparse.ArgumentParser(
                    prog='Canton User Backup Utility',
                    description='Backs up and restores user/party mappings')
        parser.add_argument('-n', '--network', choices=['devnet', 'testnet', 'mainnet'], help='Network to use')
        parser.add_argument('-c', '--command', choices=['backup_users', 'restore_users'], help='command to run')
        args = parser.parse_args()
        return UtilityArgs(args.network, args.command)
