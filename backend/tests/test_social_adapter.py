"""Where a social login lands, and which social logins are refused (authentication/adapter.py)."""

import pytest
from allauth.core.exceptions import ImmediateHttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

from authentication.adapter import MySocialAccountAdapter, is_email_allowed

pytestmark = pytest.mark.django_db


class FakeSocialLogin:
    """The parts of allauth's SocialLogin the adapter reads, after allauth's own lookup."""

    def __init__(self, user, *, process="login", existing=False, next_url=None):
        self.user = user
        self.account = f"google:{user.email}"
        self.is_existing = existing
        self.state = {"process": process}
        if next_url:
            self.state["next"] = next_url


def run_adapter(sociallogin, request_user=None):
    request = RequestFactory().get("/")
    request.user = request_user or AnonymousUser()
    MySocialAccountAdapter(request).pre_social_login(request, sociallogin)
    return sociallogin


def refused_with(sociallogin, request_user=None):
    with pytest.raises(ImmediateHttpResponse) as caught:
        run_adapter(sociallogin, request_user)
    return caught.value.response["Location"]


def new_user(email):
    return get_user_model()(username="", email=email)


def test_returning_user_goes_to_login_callback(user):
    login = run_adapter(FakeSocialLogin(user, existing=True))
    assert login.state["next"] == reverse("social-login-callback")


def test_first_login_goes_to_first_login_callback():
    login = run_adapter(FakeSocialLogin(new_user("carol@gmail.com")))
    assert login.state["next"] == reverse("social-first-login-callback")


def test_explicit_next_is_kept(user):
    login = run_adapter(FakeSocialLogin(user, existing=True, next_url="/somewhere"))
    assert login.state["next"] == "/somewhere"


def test_first_login_with_a_taken_email_is_refused(user):
    assert refused_with(FakeSocialLogin(new_user("ALICE@gmail.com"))) == reverse("duplicate-email")


def test_first_login_from_other_domain_is_refused():
    assert refused_with(FakeSocialLogin(new_user("dave@example.org"))) == reverse("invalid-email-domain")


def test_empty_domain_list_allows_any_domain(settings):
    settings.SOCIALACCOUNT_VALID_EMAIL_DOMAINS = []
    login = run_adapter(FakeSocialLogin(new_user("dave@example.org")))
    assert login.state["next"] == reverse("social-first-login-callback")


def test_connect_requires_a_signed_in_user(user):
    assert refused_with(FakeSocialLogin(user, process="connect", existing=True)) == reverse(
        "connect-social-account-without-login"
    )


def test_connect_account_owned_by_someone_else_is_refused(user, other_user):
    # Regression: this used to say "already connected by you" for every linked account.
    login = FakeSocialLogin(other_user, process="connect", existing=True)
    assert refused_with(login, request_user=user) == reverse("social-account-already-connected-by-other")


def test_connect_account_already_linked_to_me(user):
    login = FakeSocialLogin(user, process="connect", existing=True)
    assert refused_with(login, request_user=user) == reverse("social-account-already-connected-by-self")


def test_connect_checks_the_domain(user):
    login = FakeSocialLogin(new_user("eve@example.org"), process="connect")
    assert refused_with(login, request_user=user) == reverse("invalid-email-domain")


def test_connect_new_account_is_allowed(user):
    run_adapter(FakeSocialLogin(new_user("alice.other@hotmail.com"), process="connect"), request_user=user)


def test_connect_redirect_url():
    request = RequestFactory().get("/")
    assert MySocialAccountAdapter(request).get_connect_redirect_url(request, None) == reverse("social-connect-callback")


@pytest.mark.parametrize(
    ("email", "allowed"),
    [("a@gmail.com", True), ("a@GMAIL.com", True), ("a@hotmail.com", True), ("a@example.org", False), ("", False), ("no-at-sign", False)],
)
def test_is_email_allowed(email, allowed):
    assert is_email_allowed(email) is allowed
