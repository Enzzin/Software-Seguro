"""
Testa se o módulo config lê corretamente as variáveis de ambiente.
Usa monkeypatch para não depender do .env original.
"""

import os, importlib, sys
import pytest


@pytest.fixture(autouse=True)
def _clean_config_module():
    """Garante que o módulo config será recarregado limpo a cada teste."""
    if "config.config" in sys.modules:
        del sys.modules["config.config"]
    yield
    if "config.config" in sys.modules:
        del sys.modules["config.config"]


def test_default_config(monkeypatch):
    monkeypatch.setenv("FLASK_SECRET_KEY", "dummy-secret")
    monkeypatch.setenv("MAIL_SERVER", "smtp.test.com")
    monkeypatch.setenv("MAIL_PORT", "2525")
    monkeypatch.setenv("MAIL_USE_TLS", "false")
    monkeypatch.setenv("MAIL_USE_SSL", "true")
    monkeypatch.setenv("MAIL_USERNAME", "user@test.com")
    monkeypatch.setenv("MAIL_PASSWORD", "passwd123")
    monkeypatch.setenv("DATABASE_URL", "postgresql://x:y@host:5432/db")

    cfg_module = importlib.import_module("config.config")
    Config     = cfg_module.Config

    assert Config.SECRET_KEY            == "dummy-secret"
    assert Config.MAIL_SERVER           == "smtp.test.com"
    assert Config.MAIL_PORT             == 2525
    assert Config.MAIL_USE_TLS is False
    assert Config.MAIL_USE_SSL is True
    assert Config.MAIL_USERNAME         == "user@test.com"
    assert Config.MAIL_PASSWORD         == "passwd123"
    assert Config.SQLALCHEMY_DATABASE_URI.startswith("postgresql://x:y@host")
