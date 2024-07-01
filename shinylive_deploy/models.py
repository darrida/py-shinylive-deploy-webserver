import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Literal

import git
import tomllib
from pydantic import SecretStr

repo = git.Repo()

with open("shiny_deploy.toml", "rb") as f:
    toml = tomllib.load(f)
deploy_local = toml["deploy"]["local"]
deploy_server = toml["deploy"]["server"]
development: dict = toml["deploy"].get("development", {})
staging: dict = toml["deploy"].get("staging", {})
gitbranch: dict = toml["deploy"].get("gitbranch", {})


class DeployException(Exception):
    pass


@dataclass
class ShinyDeploy:
    base_url: str
    app_name: str = toml["general"]["app_name"]
    dir_deployment: str = None
    dir_development: str = development.get("directory", "src")
    dir_staging: str = staging.get("directory", "staging")
    prod_branch: str = gitbranch.get("prod", "main")
    beta_branch: str = gitbranch.get("beta", "main")
    mode: Literal["local", "test", "beta", "prod"] = None

    @property
    def deploy_name(self):
        modes = {"prod": "", "beta": "-beta", "test": "-test", "local": ""}
        return self.app_name + modes[self.mode]
    
    def __message(self):
        modes = {"prod": "PRODUCTION", "beta": "BETA", "test": "TEST", "local": "LOCAL"}
        print(
            "\n##################################"
            f"\nDEPLOYMENT MODE:   {modes[self.mode]}"
            f"\nDEPLOYMENT NAME: {self.deploy_name}"
            "\n##################################"
        )
    
    def __check_requirements(self):
        if len(sys.argv) < 2 or sys.argv[1] not in ("test", "beta", "prod", "local"):
            raise ValueError("\nERROR: One of the following arguments is required -> [ local | test | beta | prod ]\n")
        self.mode = sys.argv[1]
        if self.mode == "prod" and str(repo.active_branch) != self.prod_branch:
            raise DeployException(f"Missing Requirement: `prod` deployments can only be executed from the `{self.branches.deploy}` branch")
        elif self.mode == "beta" and str(repo.active_branch) != self.beta_branch:
            raise DeployException(f"Missing Requirement: `beta` deployments can only be executed from the `{self.branches.beta}` branch")
    
    def __compile(self):
        cmd = f"shinylive export {Path(self.dir_development)} {Path(self.dir_staging) / self.deploy_name}"
        print(f"\nExport Command: {cmd}")
        subprocess.run(cmd, shell=True, check=True)


@dataclass
class ServerShinyDeploy(ShinyDeploy):
    host: str
    user: str
    password: SecretStr
    
    def deploy(self, testing: bool = False):
        self.__check_requirements()
        self.__message()
        self.__compile()

        staging_dir = Path(self.dir_staging) / self.deploy_name
        deployment_dir = PurePosixPath(self.dir_deployment)
        # if exists:
        #     cmd = f"ssh {self.user}@{self.host} mv {target_dir} {target_dir}-backup"
        #     subprocess.run(cmd, shell=True, check=True)
        cmd = f"pscp -r -i {staging_dir}/ {self.user}@{self.host}:{deployment_dir}"  # /homes/user/docker_volumes/shinyapps/
        print(f"PSCP Command: {cmd}")
        if testing:
            return
        subprocess.run(cmd, shell=True, check=True)
        print(
            "\nCOMPLETE:"
            f"\n- `{self.app_name}` compiled and deployed to webserver"
            f"\n- App available at {self.base_url}/{self.deploy_name}"
        )

    def rollback(self):
        deployment_dir = PurePosixPath(self.dir_deployment)
        subprocess.run(f"ssh {self.user}@{self.host} rm -rf {deployment_dir}", shell=True, check=True)
        subprocess.run(f"ssh {self.user}@{self.host} mv {deployment_dir}-backup {deployment_dir}", shell=True, check=True)


class LocalShinyDeploy(ShinyDeploy):
    def deploy(self):
        self.__check_requirements()
        self.__message()
        self.__compile()

        staging_dir = Path(self.dir_staging) / self.deploy_name
        existing_deploy_dir = Path(self.dir_deployment) / self.deploy_name
        if existing_deploy_dir.exists():
            subprocess.run(f"mv {existing_deploy_dir} {existing_deploy_dir}-backup", shell=True)
        cmd = f"mv {staging_dir} {Path(self.dir_deployment)}"
        print(f"Local Move Command: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
        print(
            "\nCOMPLETE:"
            f"\n- Application `{self.app_name}` compiled and deployed locally as `{self.deploy_name}`"
            f"\n- Available at {self.base_url}/{self.deploy_name}"
        )

    def rollback(self):
        existing_deploy_dir = Path(self.dir_deployment) / self.deploy_name
        subprocess.run(f"rm -r {existing_deploy_dir}", shell=True, check=True)
        subprocess.run(f"mv {existing_deploy_dir}-backup {existing_deploy_dir}", shell=True, check=True)