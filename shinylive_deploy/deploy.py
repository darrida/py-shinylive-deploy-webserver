import subprocess
import sys
from pathlib import Path, PurePosixPath

import git
from models import DeployConfig
from pydantic import SecretStr

repo = git.Repo()


def prep_app_name(config: DeployConfig):
    if len(sys.argv) < 2 or sys.argv[1] not in ("test", "beta", "prod", "local"):
        print("\nERROR: One of the following arguments is required -> [ local | test | beta | prod ]\n")
        exit()
    config.mode = sys.argv[1]

    if config.mode == "prod":
        if str(repo.active_branch) != "main":
            print(f"ERROR: `prod` deployments can only be executed from the `{config.branches.deploy}` branch")
        show_mode = "PRODUCTION"
    elif config.mode == "beta":
        if str(repo.active_branch) != "main":
            print(f"ERROR: `prod` deployments can only be executed from the `{config.branches.beta}` branch")
        show_mode = "BETA"
    elif config.mode == "test":
        show_mode = "TEST"
    else:
        show_mode = "LOCAL"

    print("\n##################################")
    print(f"DEPLOY MODE:   {show_mode}")
    print(f"DEPLOYED NAME: {config.deploy_name}")
    print("##################################")

    return config


def shinylive_export(config: DeployConfig):
    cmd = f"shinylive export {Path(config.directories.dev)} {Path(config.directories.staging) / config.deploy_name}"
    print(f"\nExport Command: {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def local(config: DeployConfig):
    staging_dir = Path(config.directories.staging) / config.deploy_name
    existing_deploy_dir = Path(config.directories.deploy) / config.deploy_name
    if existing_deploy_dir.exists():
        subprocess.run(f"mv {existing_deploy_dir} {existing_deploy_dir}-backup", shell=True, check=True)
    cmd = f"mv {staging_dir} {Path(config.directories.deploy)}"
    print(f"Local Move Command: {cmd}")
    subprocess.run(cmd, shell=True, check=True)
    print("\nCOMPLETE:")
    print(f"- Application `{config.app_name}` compiled and deployed locally as `{config.deploy_name}`")
    print(f"- Available at {config.base_url}/{config.deploy_name}")


def local_rollback(config: DeployConfig):
    existing_deploy_dir = Path(config.directories.deploy) / config.deploy_name
    subprocess.run(f"rm -r {existing_deploy_dir}", shell=True, check=True)
    subprocess.run(f"mv {existing_deploy_dir}-backup {existing_deploy_dir}", shell=True, check=True)


def pscp(config: DeployConfig, testing: bool = False):
    staging_dir = Path(config.directories.staging) / config.deploy_name
    target_dir = PurePosixPath(config.directories.deploy)
    # if exists:
    #     cmd = f"ssh {config.user}@{config.host} mv {target_dir} {target_dir}-backup"
    #     subprocess.run(cmd, shell=True, check=True)
    cmd = f"pscp -r -i {staging_dir}/ {config.user}@{config.host}:{target_dir}"  # /homes/user/docker_volumes/shinyapps/
    print(f"PSCP Command: {cmd}")
    if testing:
        return
    subprocess.run(cmd, shell=True, check=True)
    print("\nCOMPLETE:")
    print(f"- `{config['app_name']}` compiled and deployed to webserver")
    print(f"- App available at {config.base_url}/{config.deploy_name}")


def pscp_rollback(config: DeployConfig):
    target_dir = PurePosixPath(config.directories.deploy)
    subprocess.run(f"ssh {config.user}@{config.host} rm -rf {target_dir}", shell=True, check=True)
    subprocess.run(f"ssh {config.user}@{config.host} mv {target_dir}-backup {target_dir}", shell=True, check=True)