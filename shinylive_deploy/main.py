import sys
from getpass import getpass

from models import LocalShinyDeploy, ServerShinyDeploy, toml
from pydantic import SecretStr

if __name__ == "__main__":
    if input("Server deployment (y/n)? ")  == "y":
        config = toml["deploy"]["server"]

        shinylive_ = ServerShinyDeploy(
            base_url=config["base_url"],
            dir_deployment=config["directory"],
            host=config["host"],
            user=config["user"],
            password=SecretStr(value=getpass(f"SSH password for [{config["user"]}]: "))
        )
    else:
        config = toml["deploy"]["local"]

        shinylive_ = LocalShinyDeploy(
            base_url=config["base_url"],
            dir_deployment=config["directory"]
        )
        
    if "rollback" in sys.argv:
        shinylive_.rollback()
    else:
        shinylive_.deploy()