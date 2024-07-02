from pathlib import Path


def create_config_file():
    text = """
[general]
app_name = "app1"

[development]
directory = "src_dev/app1"

[deploy.gitbranch]
prod = "main"
beta = "main"

[deploy.staging]
directory = "staging"

[deploy.local]
directory = "src_test_webserver/shinyapps/"
base_url = "localhost:8000/apps"

[deploy.server]
host = "127.0.0.1"
user = "shinylive"
port = 2222
directory = "shinyapps"
base_url = "http://localhost:5000"
"""

    with open(Path.cwd() / "shinylive_deploy.toml", "w") as f:
        f.write(text)
    