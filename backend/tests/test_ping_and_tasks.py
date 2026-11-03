"""Ping endpoint and the background task example (django-q2 runs tasks inline in tests)."""

import pytest
from django.urls import reverse
from django.utils import timezone
from django_q.models import Task
from django_q.tasks import async_task, result

from tests.conftest import needs_debug

pytestmark = [pytest.mark.django_db, needs_debug]


def test_ping(api_client):
    response = api_client.get(reverse("ping"))
    assert response.status_code == 200
    assert response.json()["response"] == "pong"


def test_job_runs_and_reports_success(api_client):
    task_id = api_client.get(reverse("ping-job")).json()["response"]
    progress = api_client.get(reverse("ping-progress", args=[task_id])).json()
    assert progress == {"state": "SUCCESS", "details": "pong"}


def test_progress_of_an_unknown_task_is_pending(api_client):
    # Regression: this used to crash with a 500 while the task was not finished.
    response = api_client.get(reverse("ping-progress", args=["not-finished-yet"]))
    assert response.status_code == 200
    assert response.json()["state"] == "PENDING"


def test_failed_task_is_reported_as_failure(api_client):
    # What the worker stores when a task raises.
    now = timezone.now()
    Task.objects.create(
        id="0" * 32, name="failed-ping", func="ping.task.ping_job", started=now, stopped=now, success=False, result="boom"
    )
    response = api_client.get(reverse("ping-progress", args=["0" * 32])).json()
    assert response == {"state": "FAILURE", "details": "boom"}


def test_task_function_directly():
    task_id = async_task("ping.task.ping_job", msg="hello")
    assert result(task_id) == "hello"


def test_websocket_page(client):
    response = client.get(reverse("ping-index"))
    assert response.status_code == 200
    assert 'data-ws-path="/ws/ping/"' in response.content.decode()
