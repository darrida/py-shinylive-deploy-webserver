import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from paramiko import AutoAddPolicy, SFTPClient, SSHClient
from pydantic import SecretStr

from .base import DeployException, ShinyDeploy, WindowsPaths

subprocess_config = {"capture_output": True, "text": True, "shell": True, "check": True}


@dataclass
class ServerShinyDeploy(ShinyDeploy):
    host: str = None
    user: str = None
    port: int = 22
    password: SecretStr = None

    @property
    def base_ssh_cmd(self):
        return f"ssh -p {self.port} {self.user}:{self.password.get_secret_value()}@{self.host}"
    
    def deploy(self, testing: bool = False):
        if not all([self.host, self.user, self.password]):
            raise ValueError("For ServerShinyDeploy, all of the following are required: host, user, password")
        self._check_git_requirements()
        self._message()
        self._compile()
        if platform.system() == 'Windows':
            app_js_path = Path(self.dir_staging) / self.deploy_name / "app.json"
            WindowsPaths.workaround(app_js_path)

        with SSHClient() as ssh:
            ssh = self._ssh_connection(ssh)
            sftp = ssh.open_sftp()

            has_backup = self._manage_backup(sftp)
            if has_backup is None:
                return
            
            self._push_app(sftp, testing)

        print(
            "\nCOMPLETE:"
            f"\n- `{self.app_name}` compiled and deployed to webserver as `{self.deploy_name}`"
            f"\n- App available at {self.base_url}/{self.deploy_name}"
        )
        if has_backup is True:
            print(f"- Backup available at {self.base_url}/{self.deploy_name}-backup")

    def rollback(self):
        self._check_git_requirements()
        deployment_dir = PurePosixPath(self.dir_deployment) / self.deploy_name

        with SSHClient() as ssh:
            ssh = self._ssh_connection(ssh)
            sftp = ssh.open_sftp()
            if not self._deployed_dir_exists(sftp):
                print("\n>>> WARNING <<<: Backback STOPPED. No app directory exists to rollback from.\n")
                return
            if not self._backup_dir_exists(sftp):
                print("\n>>> WARNING <<<: Backback STOPPED. No backup directory exists for rollback.\n")
                return
            
            ssh.exec_command(f"rm -rf {deployment_dir}")
            print(f"\n1. Removed `{self.deploy_name}`")
            ssh.exec_command(f"mv {deployment_dir}-backup {deployment_dir}")
            print(f"2. Renamed `{self.deploy_name}-backup` as `{self.deploy_name}`")

        print(
            "\nROLLBACK COMPLETE:"
            f"\n- App name: `{self.app_name}`"
            f"\n- Available at {self.base_url}/{self.deploy_name}"
        )

    def clean_rollback(self):
        self._check_git_requirements()
        deployment_dir = PurePosixPath(self.dir_deployment) / self.deploy_name

        with SSHClient() as ssh:
            ssh = self._ssh_connection(ssh)
            sftp = ssh.open_sftp()
            if not self._backup_dir_exists(sftp):
                print("\n>>> WARNING <<<: Backback STOPPED. No backup directory exists to remove.\n")
                return
            
            ssh.exec_command(f"rm -rf {deployment_dir}-backup")
            print(f"\nRemoved `{deployment_dir}-backup`")
            print("\nROLLBACK CLEANUP COMPLETE")

    def remove(self):
        self._check_git_requirements()
        deployment_dir = PurePosixPath(self.dir_deployment) / self.deploy_name

        with SSHClient() as ssh:
            ssh = self._ssh_connection(ssh)
            sftp = ssh.open_sftp()
            if not self._deployed_dir_exists(sftp):
                print("\n>>> WARNING <<<: App removal STOPPED. No app directory exists to remove.\n")
                return
            
            ssh.exec_command(f"rm -rf {deployment_dir}")
            print(f"\nRemoved `{deployment_dir}`")
            print("\nAPPLICATION REMOVAL COMPLETE")

    def _ssh_connection(self, client: SSHClient) -> SSHClient:
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(
            hostname=self.host, port=self.port, username=self.user, password=self.password.get_secret_value(), look_for_keys=False
        )
        return client

    def _deployed_dir_exists(self, sftp: SFTPClient):
        directories = sftp.listdir(str(self.dir_deployment))
        if self.deploy_name in directories:
            return True
        return False
    
    def _backup_dir_exists(self, sftp: SFTPClient):
        directories = sftp.listdir(str(self.dir_deployment))
        if f"{self.deploy_name}-backup" in directories:
            return True
        return False
    
    def _confirm_depoy_dir_exists(self, sftp: SFTPClient):
        directories = sftp.listdir()
        if str(self.dir_deployment) not in directories:
            raise DeployException(f"ACTION REQUIRED`{self.dir_deployment}` not found in the ssh target for user `{self.user}`. Create this directory, owned by this user, then try again.")
    def _manage_backup(self, sftp: SFTPClient):
        self._confirm_depoy_dir_exists(sftp)

        deployment_filepath = PurePosixPath(self.dir_deployment) / self.deploy_name
        print(deployment_filepath)
        if self._deployed_dir_exists(sftp):
            if self._backup_dir_exists(sftp):
                print(
                    "\n>>> WARNING <<<: Deployment STOPPED. Backup directory already exists. "
                    "Delete current backup directory using `shinylive_deploy <mode> --clean-rollback`, "
                    "or rollback before redeploying using `shinylive_deploy <mode> --rollback`.\n"
                )
                return None
            sftp.rename(str(deployment_filepath), f"{deployment_filepath}-backup")
            return True
        return False
    
    def _push_app(self, sftp: SFTPClient, testing: bool = False):
        staging_filepath = Path(self.dir_staging) / self.deploy_name

        sftp.mkdir(str(PurePosixPath(self.dir_deployment) / self.deploy_name))
        cmd = f"pscp -P {self.port} -r -pw <PASSWORD> {staging_filepath} {self.user}@{self.host}:{self.dir_deployment}"  # /homes/user/docker_volumes/shinyapps/
        print(f"PSCP Command: {cmd}")
        if testing:
            return
        subprocess.run(cmd.replace("<PASSWORD>", self.password.get_secret_value()), shell=True, check=True)  # noqa: S602
