import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Literal

import git
import paramiko
import tomllib
from paramiko import AutoAddPolicy, SFTPClient, SSHClient
from pydantic import SecretStr

repo = git.Repo()

with open("shiny_deploy.toml", "rb") as f:
    toml = tomllib.load(f)

deploy_local = toml["deploy"]["local"]
deploy_server = toml["deploy"]["server"]
development: dict = toml.get("development", {})
staging: dict = toml["deploy"].get("staging", {})
gitbranch: dict = toml["deploy"].get("gitbranch", {})

subprocess_config = {
    "capture_output": True, "text": True, 
    "shell": True, "check": True
}

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
    
    def _message(self):
        print(
            "\n##################################"
            f"\nDEPLOYMENT MODE: {self.mode}"
            f"\nDEPLOYMENT NAME: {self.deploy_name}"
            "\n##################################"
        )
    
    def _check_requirements(self):
        # if len(sys.argv) < 2 or sys.argv[1] not in ("test", "beta", "prod", "local"):
        #     raise ValueError("\nERROR: One of the following arguments is required -> [ local | test | beta | prod ]\n")
        # self.mode = sys.argv[1]
        if self.mode == "prod" and str(repo.active_branch) != self.prod_branch:
            raise DeployException(f"Missing Requirement: `prod` deployments can only be executed from the `{self.prod_branch}` branch")
        elif self.mode == "beta" and str(repo.active_branch) != self.beta_branch:
            raise DeployException(f"Missing Requirement: `beta` deployments can only be executed from the `{self.beta_branch}` branch")
    
    def _compile(self):
        cmd = f"shinylive export {Path(self.dir_development)} {Path(self.dir_staging) / self.deploy_name}"
        print(f"\nExport Command: {cmd}")
        subprocess.run(cmd, shell=True, check=True)

        
@dataclass
class ServerShinyDeploy(ShinyDeploy):
    host: str = None
    user: str = None
    port: int = 22
    password: SecretStr = None

    @property
    def base_ssh_cmd(self):
        return f"ssh -p {self.port} {self.user}:{self.password.get_secret_value()}@{self.host}"

    def ssh_connection(self, client: SSHClient) -> SSHClient:
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(
            hostname=self.host, port=self.port, username=self.user, password=self.password.get_secret_value()
        )
        return client

    def deployed_dir_exists(self, sftp: SFTPClient):
        existing_deploy_dir = Path(self.dir_deployment) / self.deploy_name
        # result = subprocess.run(f"{self.base_ssh_cmd} ls {self.dir_deployment}", **subprocess_config)
        # directories = result.stdout.split("\n")
        directories = sftp.listdir(str(self.dir_deployment))
        if Path(existing_deploy_dir).name in directories:
            return True
        return False
    
    def backup_dir_exists(self, sftp: SFTPClient):
        existing_deploy_dir = Path(self.dir_deployment) / self.deploy_name
        # result = subprocess.run(f"{self.base_ssh_cmd} ls {self.dir_deployment}", **subprocess_config)
        # directories = result.stdout.split("\n")
        directories = sftp.listdir(str(self.dir_deployment))
        if Path(f"{existing_deploy_dir}-backup").name in directories:
            return True
        return False
    
    def deploy(self, testing: bool = False):
        if not all([self.host, self.user, self.password]):
            raise ValueError("For ServerShinyDeploy, all of the following are required: host, user, password")
        self._check_requirements()
        self._message()
        self._compile()
    
        with SSHClient() as ssh:
            ssh = self.ssh_connection(ssh)
            sftp = ssh.open_sftp()

            staging_dir = Path(self.dir_staging) / self.deploy_name
            deployment_dir = PurePosixPath(self.dir_deployment) / self.deploy_name
            if self.deployed_dir_exists(sftp):
                if self.backup_dir_exists(sftp):
                    print("\n>>> WARNING <<<: Deployment STOPPED. Backup directory already exists. Delete backup directory, or rollback before redeploying.\n")
                    return
                # subprocess.run(f"{self.base_ssh_cmd} mv {deployment_dir} {deployment_dir}-backup", shell=True)
                sftp.rename(str(deployment_dir), f"{deployment_dir}-backup")
            # subprocess.run(f"{self.base_ssh_cmd} mkdir shinyapps/app1-test", shell=True, check=True)
            sftp.mkdir(str(deployment_dir))
            cmd = f"pscp -P {self.port} -r -pw <PASSWORD> {staging_dir} {self.user}@{self.host}:{self.dir_deployment}"  # /homes/user/docker_volumes/shinyapps/
            print(f"PSCP Command: {cmd}")
            if testing:
                return
            subprocess.run(cmd.replace("<PASSWORD>", self.password.get_secret_value()), shell=True, check=True)
        print(
            "\nCOMPLETE:"
            f"\n- `{self.app_name}` compiled and deployed to webserver"
            f"\n- App available at {self.base_url}/{self.deploy_name}"
        )

    def rollback(self):
        self._check_requirements()
        deployment_dir = PurePosixPath(self.dir_deployment) / self.deploy_name

        with SSHClient() as ssh:
            ssh = self.ssh_connection(ssh)
            sftp = ssh.open_sftp()
            if not self.deployed_dir_exists(sftp):
                print("\n>>> WARNING <<<: Backback STOPPED. No app directory exists to rollback from.\n")
                return
            if not self.backup_dir_exists(sftp):
                print("\n>>> WARNING <<<: Backback STOPPED. No backup directory exists for rollback.\n")
                return
            ssh.exec_command(f"rm -rf {deployment_dir}")
            ssh.exec_command(f"mv {deployment_dir}-backup {deployment_dir}")


class LocalShinyDeploy(ShinyDeploy):
    def deployed_dir_exists(self):
        existing_deploy_dir = Path(self.dir_deployment) / self.deploy_name
        result = subprocess.run(f"ls {self.dir_deployment}", **subprocess_config)
        directories = result.stdout.split("\n")
        if Path(existing_deploy_dir).name in directories:
            return True
        return False
    
    def backup_dir_exists(self):
        existing_deploy_dir = Path(self.dir_deployment) / self.deploy_name
        result = subprocess.run(f"ls {self.dir_deployment}", **subprocess_config)
        directories = result.stdout.split("\n")
        if Path(f"{existing_deploy_dir}-backup").name in directories:
            return True
        return False

    def deploy(self):
        self._check_requirements()
        self._message()
        self._compile()

        staging_dir = Path(self.dir_staging) / self.deploy_name
        existing_deploy_dir = Path(self.dir_deployment) / self.deploy_name
        if self.deployed_dir_exists():
            if self.backup_dir_exists():
                print("\n>>> WARNING <<<: Deployment STOPPED. Backup directory already exists. Delete backup directory, or rollback before redeploying.\n")
                return
            cmd = f"mv {existing_deploy_dir} {existing_deploy_dir}-backup"
            print(f"Backup move command: {cmd}")
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
        self._check_requirements()
        existing_deploy_dir = Path(self.dir_deployment) / self.deploy_name
        if not self.deployed_dir_exists():
            print("\n>>> WARNING <<<: Backback STOPPED. No app directory exists to rollback from.\n")
            return
        if not self.backup_dir_exists():
            print("\n>>> WARNING <<<: Backback STOPPED. No backup directory exists for rollback.\n")
            return
        subprocess.run(f"rm -r {existing_deploy_dir}", **subprocess_config)
        subprocess.run(f"mv {existing_deploy_dir}-backup {existing_deploy_dir}", **subprocess_config)


class DeployException(Exception):
    pass