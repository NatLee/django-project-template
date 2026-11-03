"""The login playground pages (DEBUG only)."""

import pytest
from django.test import Client
from django.urls import reverse

from tests.conftest import needs_debug

pytestmark = [pytest.mark.django_db, needs_debug]


def test_dashboard_explains_how_to_add_a_provider(client, settings):
    settings.SOCIALACCOUNT_PROVIDERS = {}
    html = client.get(reverse("dev-dashboard")).content.decode()
    assert "No provider configured yet" in html
    assert 'data-token-refresh-url="/api/auth/token/refresh"' in html


def test_dashboard_lists_configured_providers(client, settings):
    settings.SOCIALACCOUNT_PROVIDERS = {
        "google": {"APPS": [{"client_id": "google-id-123", "secret": "s", "settings": {}}]},
    }
    html = client.get(reverse("dev-dashboard")).content.decode()
    assert "google-id-123" in html
    assert "/api/allauth/google/login/?process=login" in html
    assert "/api/allauth/google/login/?process=connect" in html
    assert "/api/allauth/microsoft/login/" not in html


def test_session_login_and_logout(client, user, password):
    response = client.post(reverse("dev-login"), {"username": "alice", "password": password})
    assert response.status_code == 302
    assert "Signed in as <strong>alice</strong>" in client.get(reverse("dev-dashboard")).content.decode()

    client.get(reverse("dev-session-logout"))
    assert "No session yet" in client.get(reverse("dev-dashboard")).content.decode()


def test_wrong_password_shows_an_error(client, user):
    response = client.post(reverse("dev-login"), {"username": "alice", "password": "nope"})
    assert response.status_code == 200
    assert "Wrong username or password" in response.content.decode()


def test_login_form_is_csrf_protected(user, password):
    # Regression: the form used to be exempt from CSRF protection.
    strict = Client(enforce_csrf_checks=True)
    response = strict.post(reverse("dev-login"), {"username": "alice", "password": password})
    assert response.status_code == 403
