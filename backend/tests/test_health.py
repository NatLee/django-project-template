import pytest
from django.urls import reverse

from backend import health


@pytest.mark.django_db
def test_health_ok(client):
    response = client.get(reverse("health"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ok", "cache": "ok"}}
    assert "no-cache" in response["Cache-Control"]


@pytest.mark.django_db
def test_health_reports_a_failing_dependency(client, monkeypatch):
    def broken():
        raise ConnectionError("redis is down")

    monkeypatch.setitem(health.CHECKS, "cache", broken)
    response = client.get(reverse("health"))
    assert response.status_code == 503
    assert response.json()["checks"] == {"database": "ok", "cache": "error"}
    assert "redis is down" not in response.content.decode()  # no internals leak out
