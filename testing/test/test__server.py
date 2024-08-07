# ruff: noqa: S101
import shutil
from pathlib import Path

import pytest
from paramiko import SFTPClient, SSHClient
from shinylive_deploy.app import initialize

deployment_stopped_msg = (
    ">>> WARNING <<<: Deployment STOPPED. Backup directory already exists. "
    "Delete current backup directory using `shinylive_deploy <mode> --clean-rollback`, "
    "or rollback before redeploying using `shinylive_deploy <mode> --rollback`."
)


def reset_ssh_dirs(ssh: SSHClient, sftp: SFTPClient):
    # refresh ssh directories
    directories = sftp.listdir()
    if "shinyapps" in directories:
        ssh.exec_command("rm -rf shinyapps")
    ssh.exec_command("mkdir shinyapps")
    # refresh local staging directory
    staging_dir = Path(__file__).parent.parent / "staging"
    if staging_dir.exists():
        shutil.rmtree(staging_dir.resolve())
    staging_dir.mkdir()
    with open(staging_dir / ".gitignore", "w") as f: 
        f.write("*\n!.gitignore")


@pytest.fixture()
def sftp_session(monkeypatch):
    """temporarily patches the object in the test context"""
    monkeypatch.setattr('shinylive_deploy.process.getpass', lambda _: "docker")

    shinylive_ = initialize("test")
    with SSHClient() as ssh:
        ssh = shinylive_._ssh_connection(ssh)
        sftp = ssh.open_sftp()
        reset_ssh_dirs(ssh, sftp)
        yield sftp
        reset_ssh_dirs(ssh, sftp)


def test_deploy_test(capfd, sftp_session):
    mode = "test"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    out, err = capfd.readouterr()
    assert "DEPLOYMENT MODE: test" in out
    assert "DEPLOYMENT NAME: app1-test" in out
    assert "Export Command: shinylive export src staging/app1" in out
    assert "Writing staging/app1-test/app.json:" in out
    # out, err = capfd.readouterr()
    assert "COMPLETE:" in out
    assert "- `app1` compiled and deployed to webserver as `app1-test`" in out
    assert "- App available at http://localhost:5000/app1-test" in out
    assert "- Backup available at http://localhost:5000/app1-test-backup" not in out
    # confirm app was moved out of staging dir
    staging_dir = Path(__file__).parent.parent / "app1-test"
    assert staging_dir.exists() is False
    # confirm block message not displayed
    assert deployment_stopped_msg not in out
    # confirm correct existence of directories
    directories = sftp_session.listdir("shinyapps")
    assert "app1-test" in directories
    assert "app1-test-backup" not in directories


def test_deploy_test_create_backup(capfd, sftp_session):
    mode = "test"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.deploy()
    out, err = capfd.readouterr()
    assert "DEPLOYMENT MODE: test" in out
    assert "DEPLOYMENT NAME: app1-test" in out
    assert "Export Command: shinylive export src staging/app1" in out
    assert "Writing staging/app1-test/app.json:" in out
    assert "COMPLETE:" in out
    assert "- `app1` compiled and deployed to webserver as `app1-test`" in out
    assert "- App available at http://localhost:5000/app1-test" in out
    assert "- Backup available at http://localhost:5000/app1-test-backup" in out

    # confirm app was moved out of staging dir
    staging_dir = Path(__file__).parent.parent / "app1-test"
    assert staging_dir.exists() is False
    # confirm block message not displayed
    assert deployment_stopped_msg not in out
    # confirm correct existence of directories
    directories = sftp_session.listdir("shinyapps")
    assert "app1-test" in directories
    assert "app1-test-backup" in directories


def test_deploy_test_blocked(capfd, sftp_session):
    mode = "test"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message IS displayed
    assert deployment_stopped_msg in out
    staging_dir = Path(__file__).parent.parent / "staging" / "app1-test"
    assert staging_dir.exists() is True
    assert deployment_stopped_msg in out


def test_deploy_test_rollback(capfd, sftp_session):
    mode = "test"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message IS displayed
    assert deployment_stopped_msg in out
    shinylive_.rollback()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert deployment_stopped_msg not in out


def test_deploy_test_rollback_no_deployment(capfd, sftp_session):
    mode = "test"
    shinylive_ = initialize(mode)
    shinylive_.rollback()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert "\n>>> WARNING <<<: Backback STOPPED. No app directory exists to rollback from.\n\n." != out


def test_deploy_test_rollback_no_backup(capfd, sftp_session):
    mode = "test"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.rollback()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert "\n>>> WARNING <<<: Backback STOPPED. No backup directory exists for rollback.\n\n." != out


def test_deploy_test_remove(capfd, sftp_session):
    mode = "test"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.remove()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert "Removed `app1-test`"
    assert "APPLICATION REMOVAL COMPLETE" in out
    assert "\n>>> WARNING <<<: Backback STOPPED. No backup directory exists for rollback.\n\n." != out


def test_deploy_test_remove_no_app(capfd, sftp_session):
    mode = "test"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.remove()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert ">>> WARNING <<<: App removal STOPPED. No app directory exists to remove." != out


def test_deploy_prod(capfd, sftp_session):
    mode = "prod"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    out, err = capfd.readouterr()
    assert "DEPLOYMENT MODE: prod" in out
    assert "DEPLOYMENT NAME: app1" in out
    assert "Export Command: shinylive export src staging/app1" in out
    assert "Writing staging/app1/app.json:" in out
    # out, err = capfd.readouterr()
    assert "COMPLETE:" in out
    assert "- `app1` compiled and deployed to webserver as `app1`" in out
    assert "- App available at http://localhost:5000/app1" in out
    assert "- Backup available at http://localhost:5000/app1-backup" not in out
    # confirm app was moved out of staging dir
    staging_dir = Path(__file__).parent.parent / "app1"
    assert staging_dir.exists() is False
    # confirm block message not displayed
    assert deployment_stopped_msg not in out
    # confirm correct existence of directories
    directories = sftp_session.listdir("shinyapps")
    assert "app1" in directories
    assert "app1-backup" not in directories


def test_deploy_prod_create_backup(capfd, sftp_session):
    mode = "prod"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.deploy()
    out, err = capfd.readouterr()
    assert "DEPLOYMENT MODE: prod" in out
    assert "DEPLOYMENT NAME: app1" in out
    assert "Export Command: shinylive export src staging/app1" in out
    assert "Writing staging/app1/app.json:" in out
    assert "COMPLETE:" in out
    assert "- `app1` compiled and deployed to webserver as `app1`" in out
    assert "- App available at http://localhost:5000/app1" in out
    assert "- Backup available at http://localhost:5000/app1-backup" in out

    # confirm app was moved out of staging dir
    staging_dir = Path(__file__).parent.parent / "app1"
    assert staging_dir.exists() is False
    # confirm block message not displayed
    assert deployment_stopped_msg not in out
    # confirm correct existence of directories
    directories = sftp_session.listdir("shinyapps")
    assert "app1" in directories
    assert "app1-backup" in directories

def test_deploy_prod_blocked(capfd, sftp_session):
    mode = "prod"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message IS displayed
    assert deployment_stopped_msg in out
    staging_dir = Path(__file__).parent.parent / "staging" / "app1"
    assert staging_dir.exists() is True
    assert deployment_stopped_msg in out


def test_deploy_prod_rollback(capfd, sftp_session):
    mode = "prod"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message IS displayed
    assert deployment_stopped_msg in out
    shinylive_.rollback()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert deployment_stopped_msg not in out


def test_deploy_prod_rollback_no_deployment(capfd, sftp_session):
    mode = "prod"
    shinylive_ = initialize(mode)
    shinylive_.rollback()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert "\n>>> WARNING <<<: Backback STOPPED. No app directory exists to rollback from.\n\n." != out


def test_deploy_prod_rollback_no_backup(capfd, sftp_session):
    mode = "prod"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.rollback()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert "\n>>> WARNING <<<: Backback STOPPED. No backup directory exists for rollback.\n\n." != out


def test_deploy_prod_remove(capfd, sftp_session):
    mode = "prod"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.remove()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert "Removed `app1`"
    assert "APPLICATION REMOVAL COMPLETE" in out
    assert "\n>>> WARNING <<<: Backback STOPPED. No backup directory exists for rollback.\n\n." != out


def test_deploy_prod_remove_no_app(capfd, sftp_session):
    mode = "prod"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.remove()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert ">>> WARNING <<<: App removal STOPPED. No app directory exists to remove." != out


def test_deploy_beta(capfd, sftp_session):
    mode = "beta"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    out, err = capfd.readouterr()
    assert "DEPLOYMENT MODE: beta" in out
    assert "DEPLOYMENT NAME: app1-beta" in out
    assert "Export Command: shinylive export src staging/app1-beta" in out
    assert "Writing staging/app1-beta/app.json:" in out
    # out, err = capfd.readouterr()
    assert "COMPLETE:" in out
    assert "- `app1` compiled and deployed to webserver as `app1-beta`" in out
    assert "- App available at http://localhost:5000/app1-beta" in out
    assert "- Backup available at http://localhost:5000/app1-beta-backup" not in out
    # confirm app was moved out of staging dir
    staging_dir = Path(__file__).parent.parent / "app1-beta"
    assert staging_dir.exists() is False
    # confirm block message not displayed
    assert deployment_stopped_msg not in out
    # confirm correct existence of directories
    directories = sftp_session.listdir("shinyapps")
    assert "app1-beta" in directories
    assert "app1-beta-backup" not in directories


def test_deploy_beta_create_backup(capfd, sftp_session):
    mode = "beta"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.deploy()
    out, err = capfd.readouterr()
    assert "DEPLOYMENT MODE: beta" in out
    assert "DEPLOYMENT NAME: app1" in out
    assert "Export Command: shinylive export src staging/app1-beta" in out
    assert "Writing staging/app1-beta/app.json:" in out
    assert "COMPLETE:" in out
    assert "- `app1` compiled and deployed to webserver as `app1-beta`" in out
    assert "- App available at http://localhost:5000/app1-beta" in out
    assert "- Backup available at http://localhost:5000/app1-beta-backup" in out

    # confirm app was moved out of staging dir
    staging_dir = Path(__file__).parent.parent / "app1"
    assert staging_dir.exists() is False
    # confirm block message not displayed
    assert deployment_stopped_msg not in out
    # confirm correct existence of directories
    directories = sftp_session.listdir("shinyapps")
    assert "app1-beta" in directories
    assert "app1-beta-backup" in directories


def test_deploy_beta_blocked(capfd, sftp_session):
    mode = "beta"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message IS displayed
    assert deployment_stopped_msg in out
    staging_dir = Path(__file__).parent.parent / "staging" / "app1-beta"
    assert staging_dir.exists() is True
    assert deployment_stopped_msg in out


def test_deploy_beta_rollback(capfd, sftp_session):
    mode = "beta"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, err = capfd.readouterr()
    # confirm blocked message IS displayed
    assert deployment_stopped_msg in out
    shinylive_.rollback()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert deployment_stopped_msg not in out


def test_deploy_beta_rollback_no_deployment(capfd, sftp_session):
    mode = "beta"
    shinylive_ = initialize(mode)
    shinylive_.rollback()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert "\n>>> WARNING <<<: Backback STOPPED. No app directory exists to rollback from.\n\n." != out


def test_deploy_beta_rollback_no_backup(capfd, sftp_session):
    mode = "beta"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.rollback()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert "\n>>> WARNING <<<: Backback STOPPED. No backup directory exists for rollback.\n\n." != out


def test_deploy_beta_remove(capfd, sftp_session):
    mode = "beta"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.remove()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert "Removed `app1-beta`"
    assert "APPLICATION REMOVAL COMPLETE" in out
    assert "\n>>> WARNING <<<: Backback STOPPED. No backup directory exists for rollback.\n\n." != out


def test_deploy_beta_remove_no_app(capfd, sftp_session):
    mode = "beta"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.remove()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert ">>> WARNING <<<: App removal STOPPED. No app directory exists to remove." != out