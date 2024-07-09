import os
from pathlib import Path

import tomllib

CONFIG_FILEPATH = os.environ.get("SHINYLIVE_DEPLOY_CONFIG", Path.cwd() / "shinylive_deploy.toml")


toml_text = """
[general]
app_name = "app1"

[development]
directory = "src"

[deploy.gitbranch]
prod = "main"
beta = "main"

[deploy.staging]
directory = "staging"

[deploy.local]
staging_only = false
directory = "src_test_webserver/shinyapps/"
base_url = "http://localhost:8000/apps"

[deploy.server]
host = "127.0.0.1"
user = "shinylive"
port = 2222
directory = "shinyapps"
base_url = "http://localhost:5000"
"""


def create_config():
    if not CONFIG_FILEPATH.exists():
        with open(CONFIG_FILEPATH, "w") as f:
            f.write(toml_text)


def read_config() -> dict:
    if not CONFIG_FILEPATH.exists():
        create_config()
        print(f"\n>>> WARNING <<<: {CONFIG_FILEPATH.name} did not yet exist. Default config file created. Please update, then run deploy again.\n")
        exit()
    with open(CONFIG_FILEPATH, "rb") as f:
        return tomllib.load(f)


# if not CONFIG_FILEPATH.exists():
#     create_config()
toml = read_config()


class Config:
    app_name = toml["general"]["app_name"]
    deploy_local = toml["deploy"]["local"]
    deploy_server = toml["deploy"]["server"]
    development: dict = toml.get("development", {})
    staging: dict = toml["deploy"].get("staging", {})
    gitbranch: dict = toml["deploy"].get("gitbranch", {})

config = Config()
