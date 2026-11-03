import pytest
from django.conf import settings
from rest_framework.test import APIClient

PASSWORD = "correct-horse-battery-staple"

# Pages that only exist while DEBUG is on (admin, dashboard, ping examples).
needs_debug = pytest.mark.skipif(not settings.DEBUG, reason="development pages are only mounted when DEBUG is on")


@pytest.fixture
def password():
    return PASSWORD


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username="alice", email="alice@gmail.com", password=PASSWORD)


@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create_user(username="bob", email="bob@gmail.com", password=PASSWORD)


@pytest.fixture
def superuser(django_user_model):
    return django_user_model.objects.create_superuser(username="root", email="root@example.com", password=PASSWORD)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def jwt_client(user):
    """API client that sends a valid Bearer token for `user`."""
    from rest_framework_simplejwt.tokens import RefreshToken

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(user).access_token}")
    return client
