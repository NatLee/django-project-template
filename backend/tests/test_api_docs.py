"""Swagger / Redoc are for staff only."""

import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("path", ["/api/__hidden_swagger.json", "/api/__hidden_swagger.yaml"])
def test_schema_for_staff(client, superuser, settings, path):
    client.force_login(superuser)
    response = client.get(path)
    assert response.status_code == 200
    assert settings.PROJECT_NAME in response.content.decode()
    assert "/auth/token" in response.content.decode()


@pytest.mark.parametrize("path", ["/api/__hidden_swagger", "/api/__hidden_redoc"])
def test_ui_pages_for_staff(client, superuser, path):
    client.force_login(superuser)
    assert client.get(path).status_code == 200


def test_schema_hidden_from_other_users(client, user):
    client.force_login(user)
    assert client.get("/api/__hidden_swagger.json").status_code == 403
