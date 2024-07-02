import re
import shutil
import subprocess
from pathlib import Path

import pytest
from shinylive_deploy.models.base import DeployException, ShinyDeploy

subprocess_config = {"capture_output": True, "text": True, "shell": True, "check": True}


# SUPPORT FUNCTIONS
def generate_message(mode: str, name: str):
    shinylive_ = ShinyDeploy(mode=mode)
    shinylive_._message()
    return f"\n##################################\nDEPLOYMENT MODE: {mode}\nDEPLOYMENT NAME: {name}\n##################################\n"


def reset_local_dirs():
    deploy_dir = Path(__file__).parent.parent / "src_test_webserver" / "shinyapps"
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir.resolve())
    deploy_dir.mkdir()
    staging_dir = Path(__file__).parent.parent / "staging"
    if staging_dir.exists():
        shutil.rmtree(staging_dir.resolve())
    staging_dir.mkdir()

@pytest.fixture()
def dirs_session():
    reset_local_dirs()
    yield
    reset_local_dirs()


def test_message_local(capfd):
    message = generate_message("local", "app1")
    out, err = capfd.readouterr()
    assert out == message

def test_message_prod(capfd):
    message = generate_message("prod", "app1")
    out, err = capfd.readouterr()
    assert out == message

def test_message_test(capfd):
    message = generate_message("test", "app1-test")
    out, err = capfd.readouterr()
    assert out == message

def test_message_beta(capfd):
    message = generate_message("beta", "app1-beta")
    out, err = capfd.readouterr()
    assert out == message

def test_check_requirements_local_main(capfd):
    shinylive_ = ShinyDeploy(mode="local")
    subprocess.run("git checkout main", **subprocess_config)
    shinylive_._check_git_requirements()
    out, err = capfd.readouterr()
    assert out == ""

def test_check_requirements_local_dev(capfd):
    shinylive_ = ShinyDeploy(mode="local")
    subprocess.run("git checkout dev", **subprocess_config)
    shinylive_._check_git_requirements()
    out, err = capfd.readouterr()
    assert out == ""

def test_check_requirements_prod_dev(capfd):
    shinylive_ = ShinyDeploy(mode="prod")
    subprocess.run("git checkout dev", **subprocess_config)
    with pytest.raises(DeployException, match=re.escape("Missing Requirement: `prod` deployments can only be executed from the `main` branch")):
        shinylive_._check_git_requirements()

def test_check_requirements_beta_dev(capfd):
    shinylive_ = ShinyDeploy(mode="beta", beta_branch="beta")
    subprocess.run("git checkout dev", **subprocess_config)
    with pytest.raises(DeployException, match=re.escape("Missing Requirement: `beta` deployments can only be executed from the `beta` branch")):
        shinylive_._check_git_requirements()

def test_check_requirements_prod_main(capfd):
    shinylive_ = ShinyDeploy(mode="prod")
    subprocess.run("git checkout main", **subprocess_config)
    shinylive_._check_git_requirements()
    out, err = capfd.readouterr()
    assert out == ""

def test_check_requirements_beta_main(capfd):
    shinylive_ = ShinyDeploy(mode="beta")
    subprocess.run("git checkout main", **subprocess_config)
    shinylive_._check_git_requirements()
    out, err = capfd.readouterr()
    assert out == ""

def test_compile_local(capfd, dirs_session):
    shinylive_ = ShinyDeploy(mode="local")
    shinylive_._compile()
    out, err = capfd.readouterr()
    assert "Export Command: shinylive export src staging/app1" in out
    assert "Writing staging/app1/app.json" in out

def test_compile_prod(capfd, dirs_session):
    shinylive_ = ShinyDeploy(mode="prod")
    shinylive_._compile()
    out, err = capfd.readouterr()
    assert "Export Command: shinylive export src staging/app1" in out
    assert "Writing staging/app1/app.json" in out

def test_compile_test(capfd, dirs_session):
    shinylive_ = ShinyDeploy(mode="test")
    shinylive_._compile()
    out, err = capfd.readouterr()
    assert "Export Command: shinylive export src staging/app1" in out
    assert "Writing staging/app1-test/app.json" in out

def test_compile_beta(capfd, dirs_session):
    shinylive_ = ShinyDeploy(mode="beta")
    shinylive_._compile()
    out, err = capfd.readouterr()
    assert "Export Command: shinylive export src staging/app1" in out
    assert "Writing staging/app1-beta/app.json" in out