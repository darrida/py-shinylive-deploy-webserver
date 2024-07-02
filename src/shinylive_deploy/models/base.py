import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import git
import tomllib

filepath = Path.cwd() / "shinylive_deploy.toml"
if not filepath.exists():
    from shinylive_deploy.data import create_config_file
    create_config_file()

with open("shinylive_deploy.toml", "rb") as f:
    toml = tomllib.load(f)

deploy_local = toml["deploy"]["local"]
deploy_server = toml["deploy"]["server"]
development: dict = toml.get("development", {})
staging: dict = toml["deploy"].get("staging", {})
gitbranch: dict = toml["deploy"].get("gitbranch", {})


@dataclass
class ShinyDeploy:
    base_url: str = None
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
    
    def _message(self):
        print(
            "\n##################################"
            f"\nDEPLOYMENT MODE: {self.mode}"
            f"\nDEPLOYMENT NAME: {self.deploy_name}"
            "\n##################################"
        )
    
    def _check_git_requirements(self):
        repo = git.Repo()
        if self.mode == "prod" and str(repo.active_branch) != self.prod_branch:
            raise DeployException(f"Missing Requirement: `prod` deployments can only be executed from the `{self.prod_branch}` branch")
        elif self.mode == "beta" and str(repo.active_branch) != self.beta_branch:
            raise DeployException(f"Missing Requirement: `beta` deployments can only be executed from the `{self.beta_branch}` branch")
    
    def _compile(self):
        staging_dir = Path.cwd() / "staging"
        if not staging_dir.exists():
            staging_dir.mkdir()
            with open(".gitkeep", "w") as f: f.write("")
        cmd = f"shinylive export {Path(self.dir_development)} {Path(self.dir_staging) / self.deploy_name}"
        print(f"\nExport Command: {cmd}")
        subprocess.run(cmd, shell=True, check=True)


class DeployException(Exception):
    pass