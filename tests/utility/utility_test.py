import pytest
from utility import cmd_args, config, BackupUtility


def build_config():
    return config.UtilityConfig.from_dict("devnet", {
        "general": {
            "backup_file": "$stage-$network-backup.json",
            "base_url": "https://participant.$network.$stage.yourorg.dev/v1",
            "auth_url": "https://keycloak.$network.$stage.yourorg.dev/auth/realms/catalyst-canton/protocol/openid-connect/token",
        },
        "networks": {
            "devnet": {
                "stage": "dev",
                "client_id": "devnet",
            }
        }
    })

@pytest.fixture
def mock_args(monkeypatch):
    """Mock Args class"""
    args = cmd_args.UtilityArgs("devnet", "backup_users")
    def get_cmd_args():
        return args

    monkeypatch.setattr(cmd_args.UtilityArgs, "get_cmd_args", get_cmd_args)

def test_get_backup_file(mock_args):
    """Test get_backup_file returns the rendered templated backup file name"""
    utility = BackupUtility()
    configuration = build_config()
    utility.configure(configuration)
    assert utility.get_backup_file() == "dev-devnet-backup.json"
