# ruff: noqa: S101
import pytest
from pydantic import SecretStr
from shinylive_deploy.process import initialize


def test_initalize_config_local():
    config = initialize("local")
    assert config.app_name == "app1"
    assert config.deploy_name == "app1"
    assert config.mode == "local"
    assert config.base_url == "http://localhost:8000/apps"
    assert config.dir_deployment == "src_test_webserver/shinyapps/"
    assert config.dir_development == "src"
    assert config.dir_staging == "staging"
    assert config.prod_branch == "main"
    assert config.beta_branch == "main"
    with pytest.raises(AttributeError):
        assert config.host
    with pytest.raises(AttributeError):
        assert config.user
    with pytest.raises(AttributeError):
        assert config.password
    with pytest.raises(AttributeError):
        assert config.port

def test_initalize_config_prod(monkeypatch):
    """temporarily patches the object in the test context"""
    monkeypatch.setattr('shinylive_deploy.process.getpass', lambda _: "password")

    config = initialize("prod")
    assert config.app_name == "app1"
    assert config.deploy_name == "app1"
    assert config.mode == "prod"
    assert config.base_url == "http://localhost:5000"
    assert config.dir_deployment == "shinyapps"
    assert config.dir_development == "src"
    assert config.dir_staging == "staging"
    assert config.prod_branch == "main"
    assert config.beta_branch == "main"
    assert config.host == "127.0.0.1"
    assert config.user == "shinylive"
    assert isinstance(config.password, SecretStr)
    assert config.password.get_secret_value() == "password"
    assert config.port == 2222
        
def test_initalize_config_test(monkeypatch):
    """temporarily patches the object in the test context"""
    monkeypatch.setattr('shinylive_deploy.process.getpass', lambda _: "password")

    config = initialize("test")
    assert config.app_name == "app1"
    assert config.deploy_name == "app1-test"
    assert config.mode == "test"
    assert config.base_url == "http://localhost:5000"
    assert config.dir_deployment == "shinyapps"
    assert config.dir_development == "src"
    assert config.dir_staging == "staging"
    assert config.prod_branch == "main"
    assert config.beta_branch == "main"
    assert config.host == "127.0.0.1"
    assert config.user == "shinylive"
    assert isinstance(config.password, SecretStr)
    assert config.password.get_secret_value() == "password"
    assert config.port == 2222

def test_initalize_config_beta(monkeypatch):
    """temporarily patches the object in the test context"""
    monkeypatch.setattr('shinylive_deploy.process.getpass', lambda _: "password")

    config = initialize("beta")
    assert config.app_name == "app1"
    assert config.deploy_name == "app1-beta"
    assert config.mode == "beta"
    assert config.base_url == "http://localhost:5000"
    assert config.dir_deployment == "shinyapps"
    assert config.dir_development == "src"
    assert config.dir_staging == "staging"
    assert config.prod_branch == "main"
    assert config.beta_branch == "main"
    assert config.host == "127.0.0.1"
    assert config.user == "shinylive"
    assert isinstance(config.password, SecretStr)
    assert config.password.get_secret_value() == "password"
    assert config.port == 2222