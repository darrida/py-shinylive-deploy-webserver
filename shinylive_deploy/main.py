import sys
from getpass import getpass

import deploy
from models import DeployConfig, Directories, toml
from pydantic import SecretStr

if __name__ == "__main__":
    if input("Server deployment (y/n)? ")  == "y":
        config = DeployConfig(
            base_url=toml["webserver"]["base_url"],
            directories=Directories(deploy=toml["webserver"]["deploy_dir"]),
            host=toml["host"],
            user=toml["user"],
        )
        config = deploy.prep_app_name(config)
        if "rollback" in sys.argv:
            deploy.pscp_rollback(config)
        else:
            deploy.shinylive_export(config)
            password = SecretStr(value=getpass(f"SSH password for [{config.user}]: "))
            deploy.pscp(config, password, True)
    else:
        config = DeployConfig(
            base_url=toml["local"]["base_url"],
            directories=Directories(deploy=toml["local"]["deploy_dir"]),
        )
        config = deploy.prep_app_name(config)
        if "rollback" in sys.argv:
            deploy.local_rollback(config)
        else:
            deploy.shinylive_export(config)
            deploy.local(config)
