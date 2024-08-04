import re
import subprocess
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Literal

import git
from shinylive_deploy.config import config


@dataclass
class ShinyDeploy:
    base_url: str = None
    app_name: str = config.app_name
    dir_deployment: str = None
    dir_development: str = config.development.get("directory", "src")
    dir_staging: str = config.staging.get("directory", "staging")
    prod_branch: str = config.gitbranch.get("prod", "main")
    beta_branch: str = config.gitbranch.get("beta", "main")
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
        subprocess.run(cmd, shell=True, check=True)  # noqa: S602


class WindowsPaths:
    @staticmethod
    def workaround(app_js_path: Path):
        # app_file = Path(self.dir_staging) / self.deploy_name / "app.js"
        with open(app_js_path) as f:
            text = f.read()

        if path_fix_required := WindowsPaths._find_impacted(text):
            text = WindowsPaths._fix_impacted(text, path_fix_required)
            with open(app_js_path, "w") as f:
                f.write(text)
            print(f"Windows only step: fixed module paths in `{app_js_path}`")

    @staticmethod
    def _find_impacted(app_js_text: str) -> list[str]:
            matches = re.findall(r'("name": "\S*.py", "content":)', app_js_text)
            return [x for x in matches if "\\" in x]
        
    @staticmethod
    def _fix_impacted(app_js_text: str, py_module_paths: list[str]):
        def fix_path_slashes(match_obj):
            return re.sub(r"\\\\", "/", match_obj.group(1))
        
        for m in py_module_paths:
            logger = getLogger()
            logger.debug(">", m.replace('"name": "', "").replace('", "content":', ""))
        return re.sub(r'("name": "\S*.py", "content":)', fix_path_slashes, app_js_text)



class DeployException(Exception):
    pass
