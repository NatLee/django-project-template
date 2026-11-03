"""Pages that finish a social login, and the linked-accounts API."""

import json

import pytest
from allauth.socialaccount.models import SocialAccount
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken

from authentication.views import SOCIAL_EXCEPTIONS

pytestmark = pytest.mark.django_db


def tokens_in_page(response):
    """The popup page embeds the tokens with json_script; return them (or None)."""
    html = response.content.decode()
    start = html.index('<script id="social-tokens" type="application/json">') + len(
        '<script id="social-tokens" type="application/json">'
    )
    return json.loads(html[start : html.index("</script>", start)])


@pytest.mark.parametrize("name", ["social-login-callback", "social-first-login-callback"])
def test_login_callback_hands_out_tokens_for_the_session_user(client, user, name):
    client.force_login(user)
    response = client.get(reverse(name))
    assert response.status_code == 200
    tokens = tokens_in_page(response)
    assert str(AccessToken(tokens["access_token"])["user_id"]) == str(user.pk)
    assert "refresh_token" in tokens
    assert 'localStorage.setItem("loginStatus", "success")' in response.content.decode()
    assert "no-cache" in response["Cache-Control"]


def test_login_callback_without_session_has_no_tokens(client):
    response = client.get(reverse("social-login-callback"))
    assert response.status_code == 200
    assert tokens_in_page(response) is None
    assert "Not signed in" in response.content.decode()


def test_tokens_never_travel_in_the_url(client, user):
    client.force_login(user)
    response = client.get(reverse("social-login-callback"))
    assert "?tokens=" not in response.content.decode()


def test_connect_callback(client, user):
    client.force_login(user)
    response = client.get(reverse("social-connect-callback"))
    assert response.status_code == 200
    assert tokens_in_page(response) is None
    assert "Account connected" in response.content.decode()


@pytest.mark.parametrize("reason", list(SOCIAL_EXCEPTIONS))
def test_every_exception_page_renders(client, reason):
    response = client.get(reverse(reason))
    assert response.status_code == 200
    assert SOCIAL_EXCEPTIONS[reason][0] in response.content.decode()
    assert "loginStatus\", \"success" not in response.content.decode()


def test_list_and_unlink_social_accounts(jwt_client, user):
    google = SocialAccount.objects.create(user=user, provider="google", uid="g-1")
    SocialAccount.objects.create(user=user, provider="microsoft", uid="m-1")

    listed = jwt_client.get(reverse("social-account-list")).json()
    assert {a["provider"] for a in listed["social_accounts"]} == {"google", "microsoft"}

    response = jwt_client.delete(reverse("social-account-list"), {"account_id": google.id}, format="json")
    assert response.status_code == 200
    assert not SocialAccount.objects.filter(pk=google.pk).exists()


def test_unlink_needs_an_account_id(jwt_client):
    assert jwt_client.delete(reverse("social-account-list"), {}, format="json").status_code == 400


def test_cannot_unlink_someone_elses_account(jwt_client, other_user):
    theirs = SocialAccount.objects.create(user=other_user, provider="google", uid="g-2")
    response = jwt_client.delete(reverse("social-account-list"), {"account_id": theirs.id}, format="json")
    assert response.status_code == 404


def test_cannot_unlink_the_last_account_without_a_password(jwt_client, user):
    user.set_unusable_password()
    user.save()
    only = SocialAccount.objects.create(user=user, provider="google", uid="g-3")
    response = jwt_client.delete(reverse("social-account-list"), {"account_id": only.id}, format="json")
    assert response.status_code == 400
    assert SocialAccount.objects.filter(pk=only.pk).exists()


def test_session_logout_api(api_client, user):
    api_client.force_login(user)
    assert api_client.post(reverse("auth-logout")).status_code == 200
    assert api_client.get(reverse("social-account-list")).status_code in (401, 403)
