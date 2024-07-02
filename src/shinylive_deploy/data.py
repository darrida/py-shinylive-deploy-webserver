from pathlib import Path

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
directory = "src_test_webserver/shinyapps/"
base_url = "http://localhost:8000/apps"

[deploy.server]
host = "127.0.0.1"
user = "shinylive"
port = 2222
directory = "shinyapps"
base_url = "http://localhost:5000"
"""


def create_config_file():
    filepath = Path.cwd() / "shinylive_deploy.toml"
    with open(filepath, "w") as f:
        f.write(toml_text)
