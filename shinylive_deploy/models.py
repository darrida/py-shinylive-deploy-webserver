from dataclasses import dataclass
from typing import Literal

import tomllib

with open("pyproject.toml", "rb") as f:
    toml = tomllib.load(f)
toml: dict = toml["tool"]["shinylive_deploy"]


@dataclass
class Directories:
    deploy: str
    dev: str = toml.get("dev_dir", "src")
    staging: str = "staging"

@dataclass
class Branches:
    deploy: str = toml.get("deploy_branch", "main")
    beta: str = toml.get("beta_branch", "main")

@dataclass
class DeployConfig:
    base_url: str
    app_name: str = toml["app_name"]
    directories: Directories = None
    host: str = None
    user: str = None
    branches = Branches()
    mode: Literal["local", "test", "beta", "prod"] = None

    @property
    def deploy_name(self):
        if self.mode == "prod":
            return self.app_name
        if self.mode == "beta":
            return self.app_name + "-beta"
        if self.mode == "test":
            return self.app_name + "-test"
        if self.mode == "local":
            return self.app_name
        raise Exception("`DeployConfig` attribute `mode` isn't set.")
