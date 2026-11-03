"""End-to-end checks against the running Docker Compose stack, through NGINX.

Skipped unless E2E_BASE_URL is set. CI runs them inside the backend container:

    docker compose exec -e E2E_BASE_URL=http://backend-nginx \
        -e E2E_USERNAME=smoke -e E2E_PASSWORD=... backend-api pytest -m e2e

They use the real web server, the real django-q2 worker and real websockets,
so they prove what the unit tests (inline tasks, in-process ASGI) cannot.
"""

import json
import os
import time
from urllib.parse import urlparse

import pytest
import requests

BASE_URL = os.environ.get("E2E_BASE_URL", "").rstrip("/")

pytestmark = [pytest.mark.e2e, pytest.mark.skipif(not BASE_URL, reason="E2E_BASE_URL is not set")]


def url(path: str) -> str:
    return f"{BASE_URL}{path}"


@pytest.fixture(scope="module")
def access_token():
    response = requests.post(
        url("/api/auth/token"),
        json={"username": os.environ["E2E_USERNAME"], "password": os.environ["E2E_PASSWORD"]},
        timeout=10,
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_health():
    response = requests.get(url("/api/health"), timeout=10)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ok", "cache": "ok"}}


def test_frontend_is_served_by_nginx():
    response = requests.get(url("/"), timeout=10)
    assert response.status_code == 200
    assert "Your frontend goes here" in response.text


def test_static_files_are_collected_and_served():
    response = requests.get(url("/api/__hidden_statics/css/ui.css"), timeout=10)
    assert response.status_code == 200
    assert "--accent" in response.text


def test_jwt_login_and_authenticated_call(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    assert requests.post(url("/api/auth/token/verify"), json={"token": access_token}, timeout=10).status_code == 200
    me = requests.get(url("/api/allauth/social/accounts"), headers=headers, timeout=10)
    assert me.status_code == 200
    assert me.json()["username"] == os.environ["E2E_USERNAME"]


def test_api_docs_for_staff(access_token):
    response = requests.get(url("/api/__hidden_swagger.json"), headers={"Authorization": f"Bearer {access_token}"}, timeout=30)
    assert response.status_code == 200
    assert "/auth/token" in json.dumps(response.json()["paths"])


def test_background_task_is_run_by_the_worker():
    task_id = requests.get(url("/api/ping/job"), timeout=10).json()["response"]
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        progress = requests.get(url(f"/api/ping/progress/{task_id}"), timeout=10).json()
        if progress["state"] != "PENDING":
            break
        time.sleep(1)
    assert progress == {"state": "SUCCESS", "details": "pong"}


async def test_websocket_round_trip_through_nginx():
    from websockets.asyncio.client import connect

    parsed = urlparse(BASE_URL)
    ws_url = f"{'wss' if parsed.scheme == 'https' else 'ws'}://{parsed.netloc}/ws/ping/"
    async with connect(ws_url, origin=f"{parsed.scheme}://{parsed.netloc}", open_timeout=10) as socket:
        await socket.send(json.dumps({"message": "e2e"}))
        reply = json.loads(await socket.recv())
    assert reply == {"message": "e2e Pong!", "action": "ping"}
