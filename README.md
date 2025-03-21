# Canton Backup Utility

This repo provides a utility for performing Canton Validator backup and restore functions. Currently, the utility provides the capability to backup and restore Users and their rights on the Participant.

During hard migrations, the user <-> party rights mapping in validator participant is not maintained. Prior to performing a hard migration, use the provided utility to backup the existing Ledger users' rights. After the hard migration, use the utility to restore the Ledger users.

## Assumptions
The current version of this utility assumes Keycloak is used for authentication to your Canton validator, and that you have a client-id and secret with access to the `/v1/users` and `/v1/user/` APIs on the validator.

## Setup
This utility uses [Poetry](https://python-poetry.org/docs/)
```tldr
brew install pipx
pipx install poetry
poetry install
```

## Configuration

`network` refers to the Canton Network, `devnet`, `testnet`, or `mainnet`
`stage` refers to an implementation detail, such as an environment or deployment stage, e.g. `dev`, `sandbox`, `prod`
Configure the application by editing `config.tml`

### Required config values
URLs can container the placeholder values `$stage` and `$network` to make them network agnostic. All other values are static strings.

`base_url` - The base URL for all validator API requests; can be set as a common templated values or for individual networks in `config.toml`, or by environment variable
`auth_url` - The Keycloack openid-connect token URL; can be set as a common templated values or for individual networks in `config.toml`, or by environment variable
`client_id` - The client-id (created in Keycloak) used to authenticate to the validator; can be set for individual networks in `config.toml` or by environment variable

### Optional config values
`backup_file` - file name to use for backup/restore actions; Use with caution! pre-configuring this value will remove warnings about existing files when writing the backup file! can be set in the `general` section of `config.toml`
`stage` - an optional value that can be used for templating, e.g. `dev`, `sandbox`, `prod`; can only be set at the individual network level in `config.toml`
`CLIENT_SECRET` - the client secret for authenticating against the validator API. Can only be configured by environment variable
`log_level` - `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`; can be set as an environment variable `LOG_LEVEL`; defaults to `INFO`.

### Common values
Default values for all networks, set under the `general` heading in `config.toml`:
* `backup_file`
* `base_url`
* `auth_url`
* `log_level`

### Network Specific values
Network specific values, set under the `networks` subsections, e.g. `networks.devnet` in `config.toml`
* `base_url` - if provided in a network subsection, will override the common `base_url` value
* `auth_url` - if provided in a network subsection, will override the common `auth_url` value
* `client_id`
* `stage`
* `log_level`

### Environment Variables
The following values can be provided as environment variables. The utility supports [.env](https://dotenvx.com/docs/env-file) files for loading environment variables, in addition to platform specific methods of configuring environment variables. Environment variables always override statically configured values in the utility:
* `BASE_URL` - overrides `base_url`
* `AUTH_URL` - overrides `auth_url`
* `CLIENT_ID` - overrides `client_id`
* `CLIENT_SECRET`
* `LOG_LEVEL`

## Running interactively

### Backup users from the Canton Participant
`./util.sh`
Enter the desired network, eg: `devnet`
`backup_users`
On the first request, you will be prompted to enter the Client Secret. The client-secret can be found in Keycloak for the Client-id specified in the configuration. Enter the client secret found in Keycloak.

The utility will retrieve the Ledger user list and each users rights (can act/read as) from the participant, and prompt where to dump the backup. The backup filename defaults to `{stage}-{network}-users.json`, eg: `dev-devnet-users.json`.

### Restore users post migration
`./util.sh`
Enter the desired network, eg: `devnet`
`restore_users`

On the first request, you will be prompted to enter the Client Secret. The client-secret can be found in Keycloak for the Client-id specified in the configuration. Enter the client secret found in Keycloak.

The utility will prompt for the backup file to be restored. The backup file name defaults to `{stage}-{network}-users.json`, eg: `dev-devnet-users.json`.

The utility will attempt to recreate all of the users with the rights stored in the backup file.Upon completion, the utility displays which users were successfully created and which (if any) were not. It is expected that some users will fail to be created, as they will already exist. Catalyst will create some of the users automatically. If users fail to create for other reasons, the error reason should be logged.

## Running headlessly

Interactive prompts can be obviated by configuring optional values or passing in command line arguments. `util.sh` can take the optional positional arguments `network` and `command`, e.g.: `./util.sh devnet backup_users`. To run completely witout interaction, the `CLIENT_SECRET` must be set by environment variable.

## Notes
`util.sh` is a thin wrapper for invoking `src/util.py` using Python Poetry, and only allows positional arguments. More control can be exercised by invoking `util.py` directly, e.g. `poetry src/util.py --network devnet` or `poetry src/util.py --command help`.
