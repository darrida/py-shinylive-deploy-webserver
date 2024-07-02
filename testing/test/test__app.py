import re

import pytest
from pydantic import SecretStr
from shinylive_deploy.app import _initialize_configuration, _parse_arguments


def test_parse_argements_local(capfd):
    deploy_mode, rollback = _parse_arguments(["", "local"])
    assert deploy_mode == "local"
    assert rollback is False

def test_parse_argements_prod(capfd):
    deploy_mode, rollback = _parse_arguments(["", "prod"])
    assert deploy_mode == "prod"
    assert rollback is False

def test_parse_argements_test(capfd):
    deploy_mode, rollback = _parse_arguments(["", "test"])
    assert deploy_mode == "test"
    assert rollback is False

def test_parse_argements_beta(capfd):
    deploy_mode, rollback = _parse_arguments(["", "beta"])
    assert deploy_mode == "beta"
    assert rollback is False

def test_parse_argements_rollback_and_r(capfd):
    deploy_mode, rollback = _parse_arguments(["", "local", "--rollback"])
    assert deploy_mode == "local"
    assert rollback is True
    deploy_mode, rollback = _parse_arguments(["", "local", "-r"])
    assert deploy_mode == "local"
    assert rollback is True

def test_parse_argements_invalid_mode(capfd):
    with pytest.raises(ValueError, match=re.escape("\nERROR: One of the following arguments is required -> [ local | test | beta | prod ]\n")):
        _parse_arguments(["", "super"])

def test_parse_argements_invalid_rollback(capfd):
    with pytest.raises(ValueError, match=re.escape("2nd optional argument must be `-r` or `--rollback`")):
        _parse_arguments(["", "local", "rollback"])

def test_initalize_config_local():
    config = _initialize_configuration("local")
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
    monkeypatch.setattr('shinylive_deploy.app.getpass', lambda _: "password")

    config = _initialize_configuration("prod")
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
    monkeypatch.setattr('shinylive_deploy.app.getpass', lambda _: "password")

    config = _initialize_configuration("test")
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
    monkeypatch.setattr('shinylive_deploy.app.getpass', lambda _: "password")

    config = _initialize_configuration("beta")
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