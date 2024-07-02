import subprocess
from pathlib import Path

from .base import ShinyDeploy

subprocess_config = {"capture_output": True, "text": True, "shell": True, "check": True}

class LocalShinyDeploy(ShinyDeploy):
    def deploy(self):
        self._check_requirements()
        self._message()
        self._compile()

        has_backup = self.__manage_backup()
        if has_backup is None:
            return

        staging_dir = Path(self.dir_staging) / self.deploy_name
        subprocess.run(f"mv {staging_dir} {Path(self.dir_deployment)}", shell=True, check=True)
        
        print(
            "\nCOMPLETE:"
            f"\n- Application `{self.app_name}` compiled and deployed locally as `{self.deploy_name}`"
            f"\n- Available at {self.base_url}/{self.deploy_name}"
            f"\n- Backup available at {self.base_url}/{self.deploy_name}-backup" if has_backup is True else ""
        )

    def rollback(self):
        self._check_requirements()
        existing_deploy_dir = Path(self.dir_deployment) / self.deploy_name
        if not self.__deployed_dir_exists():
            print("\n>>> WARNING <<<: Backback STOPPED. No app directory exists to rollback from.\n")
            return
        if not self.__backup_dir_exists():
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

    def __deployed_dir_exists(self):
        result = subprocess.run(f"ls {self.dir_deployment}", **subprocess_config)
        directories = result.stdout.split("\n")
        if Path(self.deploy_name).name in directories:
            return True
        return False
    
    def __backup_dir_exists(self):
        result = subprocess.run(f"ls {self.dir_deployment}", **subprocess_config)
        directories = result.stdout.split("\n")
        if Path(f"{self.deploy_name}-backup").name in directories:
            return True
        return False
    
    def __manage_backup(self):
        existing_deploy_dir = Path(self.dir_deployment) / self.deploy_name
        if self.__deployed_dir_exists():
            if self.__backup_dir_exists():
                print("\n>>> WARNING <<<: Deployment STOPPED. Backup directory already exists. Delete backup directory, or rollback before redeploying.\n")
                return None
            subprocess.run(f"mv {existing_deploy_dir} {existing_deploy_dir}-backup", shell=True)
            return True
        return False
