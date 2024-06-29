import sys
from getpass import getpass
from pathlib import Path, PurePosixPath

import git
import tomllib
from pydantic import SecretStr

repo = git.Repo()

print(repo.head)
exit()
if len(sys.argv) < 2:
    mode = "test"
elif sys.argv[1] == "prod":
    mode = "prod"

with open("pyproject.toml", "rb") as f:
    config = tomllib.load(f)
config: dict = config["tool"]["shinylive_pscp_deploy"]


def export_cmd(app_name: str, staging_dir: str, dev_dir: str):
    if mode == "test":
        app_name = f"{app_name}-test"
    return f"shinylive export {Path(dev_dir) / app_name} {Path(staging_dir)}"


def pscp_cmd(app_name: str, target_dir: str, host: str, user: str, password: SecretStr, staging_dir: str):
    if mode == "test":
        app_name = f"{app_name}-test"
    staging_dir = Path(staging_dir) / app_name
    target_dir = PurePosixPath(target_dir)
    return f"pscp -r -i {staging_dir} {user}:{password.get_secret_value()}@{host}:{target_dir}"  # /homes/user/docker_volumes/shinyapps/


password = SecretStr(value=getpass(f"Input password for {config['user']}: "))

print(export_cmd(config["app_name"], config.get("staging_dir"), config.get("dev_dir")))
print(pscp_cmd(config["app_name"], config["target_dir"], config["host"], config["user"], password, config.get("staging_dir")))
