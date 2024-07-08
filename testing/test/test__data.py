# ruff: noqa: S101
from pathlib import Path

import tomllib
from shinylive_deploy.config import create_config


# TESTS
def test_create_config_file():
    create_config()
    with open(Path.cwd() / "shinylive_deploy.toml", 'rb') as f:
        toml = tomllib.load(f)
    assert toml["general"]["app_name"] == "app1"
    assert toml["development"]["directory"] == "src"
    assert toml["deploy"]["gitbranch"]["prod"] == "main"
    assert toml["deploy"]["gitbranch"]["beta"] == "main"
    assert toml["deploy"]["staging"]["directory"] == "staging"
    assert toml["deploy"]["local"]["directory"] == "src_test_webserver/shinyapps/"
    assert toml["deploy"]["local"]["base_url"] == "http://localhost:8000/apps"
    assert toml["deploy"]["server"]["host"] == "127.0.0.1"
    assert toml["deploy"]["server"]["user"] == "shinylive"
    assert toml["deploy"]["server"]["port"] == 2222
    assert toml["deploy"]["server"]["directory"] == "shinyapps"
    assert toml["deploy"]["server"]["base_url"] == "http://localhost:5000"