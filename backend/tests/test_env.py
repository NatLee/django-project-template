"""Settings come from environment variables; these helpers parse them."""

import pytest
from django.core.exceptions import ImproperlyConfigured

from backend.env import env_bool, env_int, env_list, env_str


@pytest.mark.parametrize("raw", ["true", "True", "TRUE", "1", "yes", "on"])
def test_env_bool_true(monkeypatch, raw):
    monkeypatch.setenv("FLAG", raw)
    assert env_bool("FLAG") is True


@pytest.mark.parametrize("raw", ["false", "False", "0", "no", "off"])
def test_env_bool_false(monkeypatch, raw):
    monkeypatch.setenv("FLAG", raw)
    assert env_bool("FLAG", True) is False


def test_env_bool_default_when_missing_or_empty(monkeypatch):
    monkeypatch.delenv("FLAG", raising=False)
    assert env_bool("FLAG", True) is True
    monkeypatch.setenv("FLAG", "")
    assert env_bool("FLAG", False) is False


def test_env_bool_rejects_garbage(monkeypatch):
    monkeypatch.setenv("FLAG", "maybe")
    with pytest.raises(ImproperlyConfigured, match="FLAG"):
        env_bool("FLAG")


def test_env_int(monkeypatch):
    monkeypatch.setenv("NUM", "42")
    assert env_int("NUM", 1) == 42
    monkeypatch.setenv("NUM", "forty")
    with pytest.raises(ImproperlyConfigured):
        env_int("NUM", 1)


def test_env_list(monkeypatch):
    monkeypatch.setenv("HOSTS", " a.com, b.com ,,")
    assert env_list("HOSTS") == ["a.com", "b.com"]
    monkeypatch.delenv("HOSTS")
    assert env_list("HOSTS", "x,y") == ["x", "y"]
    assert env_list("HOSTS") == []


def test_env_str_required(monkeypatch):
    monkeypatch.delenv("MISSING", raising=False)
    with pytest.raises(ImproperlyConfigured, match="MISSING"):
        env_str("MISSING", required=True)
    assert env_str("MISSING", "fallback") == "fallback"
