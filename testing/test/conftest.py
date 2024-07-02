import shutil
import subprocess
from pathlib import Path

from shinylive_deploy.data import create_config_file

create_config_file()

def pytest_sessionstart(session):
    """Execute before all tests"""
    subprocess_config = {"capture_output": True, "text": True, "shell": True, "check": True}
    # init .git session
    git_dir = Path(__file__).parent.parent / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir.resolve())
    subprocess.run("git config --global init.defaultBranch main", **subprocess_config)
    subprocess.run("git init .", **subprocess_config)
    subprocess.run('git config --global user.name "test-name"', **subprocess_config)
    subprocess.run('git config --global user.email "test@email.com"', **subprocess_config)
    subprocess.run('git add . && git commit -m "committing initial files so branch can be changed"', **subprocess_config)
    subprocess.run("git branch dev", **subprocess_config)
    # subprocess.run("git branch main", **subprocess_config)
    # subprocess.run("git checkout main", **subprocess_config)
    # create config file

    

def pytest_sessionfinish(session, exitstatus):
    """Execute after all tests complete"""
    # remove config file
    config_filepath = Path(__file__).parent.parent / "shinylive_deploy.toml"
    if config_filepath.exists():
        config_filepath.unlink()
    # remove .git directory
    git_dir = Path(__file__).parent.parent / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir.resolve())
    # remove app1 staging directory
    staging_app_dir = Path(__file__).parent.parent / "staging" / "app1"
    if staging_app_dir.exists():
        shutil.rmtree(staging_app_dir.resolve())
    staging_app_dir = Path(__file__).parent.parent / "staging" / "app1-test"
    if staging_app_dir.exists():
        shutil.rmtree(staging_app_dir.resolve())
    staging_app_dir = Path(__file__).parent.parent / "staging" / "app1-beta"
    if staging_app_dir.exists():
        shutil.rmtree(staging_app_dir.resolve())