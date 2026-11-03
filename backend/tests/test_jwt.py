import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken

pytestmark = pytest.mark.django_db


def test_obtain_returns_renamed_keys_and_username(api_client, user, password):
    response = api_client.post(reverse("token_get"), {"username": "alice", "password": password}, format="json")
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"access_token", "refresh_token", "username"}
    assert data["username"] == "alice"
    assert str(AccessToken(data["access_token"])["user_id"]) == str(user.pk)


def test_obtain_rejects_wrong_password(api_client, user):
    response = api_client.post(reverse("token_get"), {"username": "alice", "password": "nope"}, format="json")
    assert response.status_code == 401


def test_refresh_and_verify(api_client, user, password):
    tokens = api_client.post(reverse("token_get"), {"username": "alice", "password": password}, format="json").json()

    refreshed = api_client.post(reverse("token_refresh"), {"refresh": tokens["refresh_token"]}, format="json")
    assert refreshed.status_code == 200
    assert set(refreshed.json()) == {"access_token"}

    verified = api_client.post(reverse("token_verify"), {"token": refreshed.json()["access_token"]}, format="json")
    assert verified.status_code == 200


def test_bearer_token_authenticates_api_calls(jwt_client):
    response = jwt_client.get(reverse("social-account-list"))
    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_api_requires_authentication(api_client):
    assert api_client.get(reverse("social-account-list")).status_code == 401
