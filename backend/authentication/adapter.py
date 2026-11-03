"""allauth adapters: decide where a social login lands and which logins are allowed.

After a social login allauth signs the user into a Django session and redirects
to `sociallogin.state["next"]`. We point that at our callback pages, which turn
the session into a JWT for the single-page frontend (see views.py).
"""

import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.base import AuthProcess
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)


def is_email_allowed(email: str | None) -> bool:
    """True when the email's domain is in SOCIALACCOUNT_VALID_EMAIL_DOMAINS (empty list = any domain)."""
    if not email or "@" not in email:
        logger.warning("Social login without a usable email: %r", email)
        return False
    allowed = {domain.lower() for domain in settings.SOCIALACCOUNT_VALID_EMAIL_DOMAINS}
    domain = email.rpartition("@")[2].lower()
    if allowed and domain not in allowed:
        logger.warning("Social login from a domain that is not allowed: %s", email)
        return False
    return True


def fail(url_name: str):
    """Stop the allauth flow and show one of our error pages instead."""
    raise ImmediateHttpResponse(redirect(url_name))


class MyAccountAdapter(DefaultAccountAdapter):
    """Plain allauth account behaviour; kept so projects have one place to customise it."""


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # allauth has already looked the social account up: `is_existing` is True when
        # this Google/Microsoft account is linked to a user here, and `sociallogin.user`
        # is then that user.
        process = sociallogin.state.get("process")
        email = user_email(sociallogin.user)

        if process == AuthProcess.CONNECT:
            self._check_connect(request, sociallogin, email)
        elif sociallogin.is_existing:
            # Returning user: let them in and hand out tokens.
            sociallogin.state.setdefault("next", reverse("social-login-callback"))
        else:
            # First login: refuse emails that already belong to someone, or domains we don't accept.
            if email and get_user_model().objects.filter(email__iexact=email).exists():
                logger.warning("Duplicate email during social signup: %s", email)
                fail("duplicate-email")
            if email and not is_email_allowed(email):
                fail("invalid-email-domain")
            sociallogin.state.setdefault("next", reverse("social-first-login-callback"))

        return super().pre_social_login(request, sociallogin)

    def _check_connect(self, request, sociallogin, email):
        if not request.user.is_authenticated:
            logger.warning("Anonymous user tried to connect a social account")
            fail("connect-social-account-without-login")
        if sociallogin.is_existing:
            if sociallogin.user != request.user:
                logger.warning("Social account %s already belongs to another user", sociallogin.account)
                fail("social-account-already-connected-by-other")
            fail("social-account-already-connected-by-self")
        if not is_email_allowed(email):
            fail("invalid-email-domain")

    def get_connect_redirect_url(self, request, socialaccount):
        return reverse("social-connect-callback")
