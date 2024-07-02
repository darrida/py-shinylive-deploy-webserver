import sys
from getpass import getpass
from pathlib import Path

from pydantic import SecretStr
from shinylive_deploy.models import LocalShinyDeploy, ServerShinyDeploy, toml


def main():
    config_file = Path.cwd() / "shinylive_deploy.toml"
    if not config_file.exists():
        from shinylive_deploy.data import create_config_file
        create_config_file()
        return

    mode, rollback = _parse_arguments()
    shinylive_ = _initialize_configuration(mode)
    
    if rollback is True:
        shinylive_.rollback()
    else:
        shinylive_.deploy()


def _parse_arguments(test_argvs: list = None) -> tuple[str, bool]:
    if test_argvs:
        sys.argv = test_argvs
    if len(sys.argv) < 2 or sys.argv[1] not in ("test", "beta", "prod", "local"):
        raise ValueError("\nERROR: One of the following arguments is required -> [ local | test | beta | prod ]\n")
    deploy_mode = sys.argv[1]
    try:
        rollback = sys.argv[2]
        if rollback not in ("-r", "--rollback"):
            raise ValueError("2nd optional argument must be `-r` or `--rollback`")
        rollback = True
    except IndexError:
        rollback = False
    return deploy_mode, rollback


def _initialize_configuration(deploy_mode: str) -> LocalShinyDeploy | ServerShinyDeploy:
    if deploy_mode in ("test", "beta", "prod"):
        config = toml["deploy"]["server"]
        return ServerShinyDeploy(
            mode=deploy_mode,
            base_url=config["base_url"],
            dir_deployment=config["directory"],
            host=config["host"],
            user=config["user"],
            port=config.get("port", 22),
            password=SecretStr(value=getpass(f"SSH password for [{config["user"]}]: "))
        )
    else:  # local
        config = toml["deploy"]["local"]
        return LocalShinyDeploy(
            mode=deploy_mode,
            base_url=config["base_url"],
            dir_deployment=config["directory"]
        )


if __name__ == "__main__":
    main()