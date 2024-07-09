from getpass import getpass

from pydantic import SecretStr
from shinylive_deploy.config import CONFIG_FILEPATH, create_config
from shinylive_deploy.config import config as loaded_config

from .local import LocalShinyDeploy
from .server import ServerShinyDeploy


def initialize(deploy_mode: str) -> LocalShinyDeploy | ServerShinyDeploy:
    if deploy_mode not in ("local", "test", "beta", "prod"):
        raise ValueError('`DEPLOY_MODE` must be on of the following: "local", "test", "beta", "prod"')

    if not CONFIG_FILEPATH.exists():
        create_config()
        return
    if deploy_mode in ("test", "beta", "prod"):
        config = loaded_config.deploy_server
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
        config = loaded_config.deploy_local
        return LocalShinyDeploy(
            mode=deploy_mode,
            base_url=config["base_url"],
            dir_deployment=config["directory"],
            staging_only=config.get("staging_only", False)
        )