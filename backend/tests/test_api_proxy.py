"""API proxy: /api/proxy/<resource> is forwarded to {API_URL}api/<resource> with the caller's info."""

import pytest
import requests

pytestmark = pytest.mark.django_db


class FakeResponse:
    def __init__(self, data, status=200):
        self.data, self.status_code = data, status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")

    def json(self):
        return self.data


@pytest.fixture
def upstream(monkeypatch, settings):
    settings.API_URL = "http://upstream:9999/"
    calls = []

    def fake_request(method, url, **kwargs):
        calls.append({"method": method, "url": url, **kwargs})
        return FakeResponse({"ok": True, "echo": kwargs.get("json") or kwargs.get("params")})

    monkeypatch.setattr(requests, "request", fake_request)
    return calls


def test_get_is_forwarded_with_user_info(jwt_client, upstream, user):
    user.userprofile.displayname = "Alice"
    user.userprofile.save()
    response = jwt_client.get("/api/proxy/items/42?colour=red")
    assert response.status_code == 200
    call = upstream[0]
    # Regression: the target URL used to come out as ".../apiapi/items/42".
    assert call["url"] == "http://upstream:9999/api/items/42"
    assert call["params"]["colour"] == ["red"]
    assert call["params"]["username"] == "alice"
    assert call["params"]["displayname"] == "Alice"
    assert call["headers"] == {"version": "v1"}
    assert call["verify"] is True


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_body_methods_forward_json(jwt_client, upstream, method):
    response = getattr(jwt_client, method)("/api/proxy/items", {"name": "pen"}, format="json")
    assert response.status_code == 200
    assert upstream[0]["method"] == method.upper()
    assert upstream[0]["json"]["name"] == "pen"
    assert upstream[0]["json"]["username"] == "alice"


def test_upstream_failure_becomes_502(jwt_client, monkeypatch, settings):
    settings.API_URL = "http://upstream:9999/"

    def boom(*args, **kwargs):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(requests, "request", boom)
    response = jwt_client.get("/api/proxy/items")
    assert response.status_code == 502
    assert response.json()["status"] == "error"


def test_missing_api_url_is_explained(jwt_client, settings):
    settings.API_URL = ""
    response = jwt_client.get("/api/proxy/items")
    assert response.status_code == 503
    assert "API_URL" in response.json()["message"]


def test_anonymous_callers_are_refused(api_client, upstream):
    assert api_client.get("/api/proxy/items").status_code in (401, 403)
    assert upstream == []
