# ruff: noqa: S101
import shutil
from pathlib import Path

import pytest
from shinylive_deploy.process import initialize

deployment_stopped_msg = (
    ">>> WARNING <<<: Deployment STOPPED. Backup directory already exists. "
    "Delete current backup directory using `shinylive_deploy <mode> --clean-rollback`, "
    "or rollback before redeploying using `shinylive_deploy <mode> --rollback`."
)


def reset_local_dirs():
    deploy_dir = Path(__file__).parent.parent / "src_test_webserver" / "shinyapps"
    staging_dir = Path(__file__).parent.parent / "staging"

    if deploy_dir.exists():
        shutil.rmtree(deploy_dir.resolve())
    if staging_dir.exists():
        shutil.rmtree(staging_dir.resolve())
    
    deploy_dir.mkdir()
    staging_dir.mkdir()

    with open(deploy_dir / ".gitignore", "w") as f: 
        f.write("*\n!.gitignore")
    with open(staging_dir / ".gitignore", "w") as f: 
        f.write("*\n!.gitignore")


@pytest.fixture()
def dirs_session():
    reset_local_dirs()
    yield
    reset_local_dirs()


def test_deploy_local(capfd, dirs_session):
    mode = "local"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    out, _ = capfd.readouterr()
    assert "DEPLOYMENT MODE: local" in out
    assert "DEPLOYMENT NAME: app1" in out
    assert "Export Command: shinylive export src staging/app1" in out
    assert "Writing staging/app1/app.json:" in out
    assert "COMPLETE:" in out
    assert "- `app1` compiled and deployed locally as `app1`" in out
    assert "- Available at http://localhost:8000/apps/app1" in out
    assert "- Backup available at http://localhost:8000/apps/app1-backup" not in out
    # confirm app was moved out of staging dir
    staging_dir = Path(__file__).parent.parent / "app1"
    assert staging_dir.exists() is False
    # confirm app was moved into deploy dir
    deploy_dir = Path(__file__).parent.parent / "src_test_webserver" / "shinyapps" / "app1"
    assert deploy_dir.exists() is True
    assert Path(deploy_dir / "app.json").exists() is True
    assert Path(deploy_dir / "app1-backup").exists() is False


def test_deploy_local_create_backup(capfd, dirs_session):
    mode = "local"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.deploy()
    out, _ = capfd.readouterr()
    assert "DEPLOYMENT MODE: local" in out
    assert "DEPLOYMENT NAME: app1" in out
    assert "Export Command: shinylive export src staging/app1" in out
    assert "Writing staging/app1/app.json:" in out
    assert "COMPLETE:" in out
    assert "- `app1` compiled and deployed locally as `app1`" in out
    assert "- Available at http://localhost:8000/apps/app1" in out
    assert "- Backup available at http://localhost:8000/apps/app1-backup" in out

    # confirm app was moved out of staging dir
    staging_dir = Path(__file__).parent.parent / "app1"
    assert staging_dir.exists() is False
    # confirm block message not displayed
    assert deployment_stopped_msg not in out
    # confirm correct existence of directories
    deploy_dir = Path(__file__).parent.parent / "src_test_webserver" / "shinyapps"
    assert Path(deploy_dir / "app1").exists() is True
    assert Path(deploy_dir / "app1" / "app.json").exists() is True
    assert Path(deploy_dir / "app1-backup").exists() is True
    assert Path(deploy_dir / "app1-backup" / "app.json").exists() is True


def test_deploy_local_blocked(capfd, dirs_session):
    mode = "local"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    out, _ = capfd.readouterr()
    # confirm blocked message NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, _ = capfd.readouterr()
    # confirm blocked message IS displayed
    assert deployment_stopped_msg in out
    staging_dir = Path(__file__).parent.parent / "staging" / "app1"
    assert staging_dir.exists() is True
    assert deployment_stopped_msg in out


def test_deploy_local_rollback(capfd, dirs_session):
    mode = "local"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    out, _ = capfd.readouterr()
    # confirm blocked message NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert deployment_stopped_msg not in out
    shinylive_.deploy()
    out, _ = capfd.readouterr()
    # confirm blocked message IS displayed
    assert deployment_stopped_msg in out
    shinylive_.rollback()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert deployment_stopped_msg not in out


def test_deploy_local_rollback_no_deployment(capfd, dirs_session):
    mode = "local"
    shinylive_ = initialize(mode)
    shinylive_.rollback()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert "\n>>> WARNING <<<: Backback STOPPED. No app directory exists to rollback from.\n\n." != out


def test_deploy_local_rollback_no_backup(capfd, dirs_session):
    mode = "local"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.rollback()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert "\n>>> WARNING <<<: Backback STOPPED. No backup directory exists for rollback.\n\n." != out


def test_deploy_local_remove(capfd, dirs_session):
    mode = "local"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.remove()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert "Removed `app1`"
    assert "APPLICATION REMOVAL COMPLETE" in out
    assert "\n>>> WARNING <<<: Backback STOPPED. No backup directory exists for rollback.\n\n." != out


def test_deploy_local_remove_no_app(capfd, dirs_session):
    mode = "local"
    shinylive_ = initialize(mode)
    shinylive_.deploy()
    shinylive_.remove()
    out, _ = capfd.readouterr()
    # confirm blocked message still NOT displayed
    assert ">>> WARNING <<<: App removal STOPPED. No app directory exists to remove." != out
