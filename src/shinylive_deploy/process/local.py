# ruff: noqa: S602 S603
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .base import ShinyDeploy, WindowsPaths

subprocess_config = {"capture_output": True, "text": True, "shell": True, "check": True}

@dataclass
class LocalShinyDeploy(ShinyDeploy):
    staging_only: bool = False

    def deploy(self):
        self._check_git_requirements()
        self._message()
        self._compile()
        if platform.system() == 'Windows':
            app_js_path = Path(self.dir_staging) / self.deploy_name / "app.json"
            WindowsPaths.workaround(app_js_path)

        if self.staging_only in ("true", True):
            print(
                "\nCOMPLETE:"
                "\n- deployed to 'staging' folder only."
                "\n- To test: `python -m http.server -d staging --bind localhost 8008`")
            return

        has_backup = self._manage_backup()
        if has_backup is None:
            return

        staging_dir = Path(self.dir_staging) / self.deploy_name
        subprocess.run(f"mv {staging_dir} {Path(self.dir_deployment)}", shell=True, check=True)
        
        print(
            "\nCOMPLETE:"
            f"\n- `{self.app_name}` compiled and deployed locally as `{self.deploy_name}`"
            f"\n- Available at {self.base_url}/{self.deploy_name}"
        )
        if has_backup:
            print(f"- Backup available at {self.base_url}/{self.deploy_name}-backup")

    def rollback(self):
        self._check_git_requirements()
        existing_deploy_dir = Path(self.dir_deployment) / self.deploy_name
        if not self._deployed_dir_exists():
            print("\n>>> WARNING <<<: Backback STOPPED. No app directory exists to rollback to.\n")
            return
        if not self._backup_dir_exists():
            print("\n>>> WARNING <<<: Backback STOPPED. No backup directory exists for rollback.\n")
            return
        subprocess.run(f"rm -r {existing_deploy_dir}", **subprocess_config)
        print(f"\n1. Removed `{self.deploy_name}`")
        subprocess.run(f"mv {existing_deploy_dir}-backup {existing_deploy_dir}", **subprocess_config)
        print(f"2. Renamed `{self.deploy_name}-backup` as `{self.deploy_name}`")

        print(
            "\nROLLBACK COMPLETE:"
            f"\n- Application `{self.app_name}` rolled back locally as `{self.deploy_name}`"
            f"\n- Available at {self.base_url}/{self.deploy_name}"
        )

    def clean_rollback(self):
        self._check_git_requirements()
        existing_deploy_dir = Path(self.dir_deployment) / self.deploy_name
        if not self._backup_dir_exists():
            print("\n>>> WARNING <<<: Rollback cleanup STOPPED. No backup directory exists to remove.\n")
            return
        subprocess.run(f"rm -r {existing_deploy_dir}-backup", **subprocess_config)
        print(f"\nRemoved `{self.base_url}/{self.deploy_name}-backup`")
        print("\nROLLBACK CLEANUP COMPLETE")

    def remove(self):
        self._check_git_requirements()
        self._check_git_requirements()
        existing_deploy_dir = Path(self.dir_deployment) / self.deploy_name
        if not self._deployed_dir_exists():
            print("\n>>> WARNING <<<: App removal STOPPED. No app directory exists to remove.\n")
            return
        subprocess.run(f"rm -r {existing_deploy_dir}", **subprocess_config)
        print(f"\nRemoved `{self.deploy_name}`")
        print("\nAPPLICATION REMOVAL COMPLETE")

    def _deployed_dir_exists(self):
        deploy_dirs = [x.name for x in Path(self.dir_deployment).iterdir()]
        # result = subprocess.run(f"ls {self.dir_deployment}", **subprocess_config)
        # directories = result.stdout.split("\n")
        if Path(self.deploy_name).name in deploy_dirs:
            return True
        return False
    
    def _backup_dir_exists(self):
        deploy_dirs = [x.name for x in Path(self.dir_deployment).iterdir()]
        # result = subprocess.run(f"ls {self.dir_deployment}", **subprocess_config)
        # directories = result.stdout.split("\n")
        if Path(f"{self.deploy_name}-backup").name in deploy_dirs:
            return True
        return False
    
    def _manage_backup(self):
        existing_deploy_dir = Path(self.dir_deployment) / self.deploy_name
        if self._deployed_dir_exists():
            if self._backup_dir_exists():
                print(
                    "\n>>> WARNING <<<: Deployment STOPPED. Backup directory already exists. "
                    "Delete current backup directory using `shinylive_deploy <mode> --clean-rollback`, "
                    "or rollback before redeploying using `shinylive_deploy <mode> --rollback`.\n"
                )
                return None
            subprocess.run(f"mv {existing_deploy_dir} {existing_deploy_dir}-backup", shell=True)
            return True
        return False
