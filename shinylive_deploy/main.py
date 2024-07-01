import sys
from getpass import getpass

from models import LocalShinyDeploy, ServerShinyDeploy, toml
from pydantic import SecretStr

if __name__ == "__main__":
    # parse arguments
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

    # initialize configuration
    if deploy_mode in ("test", "beta", "prod"):
        config = toml["deploy"]["server"]
        shinylive_ = ServerShinyDeploy(
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
        shinylive_ = LocalShinyDeploy(
            mode=deploy_mode,
            base_url=config["base_url"],
            dir_deployment=config["directory"]
        )
        
    # execute deployment change
    if rollback is True:
        shinylive_.rollback()
    else:
        shinylive_.deploy()