"""Admin pages: login history chart, user profiles with import/export and history."""

import pytest
from django.urls import reverse

from django_login_history.models import Login
from tests.conftest import needs_debug

pytestmark = [pytest.mark.django_db, needs_debug]


@pytest.fixture
def admin_client(client, superuser):
    client.force_login(superuser)
    return client


def test_admin_index_uses_the_project_name(admin_client, settings):
    response = admin_client.get(reverse("admin:index"))
    assert response.status_code == 200
    html = response.content.decode()
    assert f"{settings.PROJECT_NAME} admin" in html
    assert "/sites/" not in html  # the Sites app is hidden


def test_login_history_list_shows_the_chart(admin_client, superuser):
    Login.objects.create(user=superuser, ip="8.8.8.8", user_agent="test")
    response = admin_client.get(reverse("admin:django_login_history_login_changelist"))
    assert response.status_code == 200
    html = response.content.decode()
    assert 'id="loginChart"' in html
    assert "chart.js@4.5.1" in html


def test_login_history_is_read_only(admin_client):
    assert admin_client.get(reverse("admin:django_login_history_login_add")).status_code == 403


def test_chart_data_endpoint(admin_client):
    url = reverse("admin:login_chart_data")
    ok = admin_client.get(url, {"start_date": "2026-01-01", "end_date": "2026-01-03"})
    assert ok.status_code == 200
    assert len(ok.json()) == 3  # one user (the superuser), three days
    bad = admin_client.get(url, {"start_date": "yesterday"})
    assert bad.status_code == 400


def test_user_profile_admin_has_import_export_and_history(admin_client, superuser):
    profile = superuser.userprofile
    profile.displayname = "Root"
    profile.save()

    changelist = admin_client.get(reverse("admin:userprofile_userprofile_changelist")).content.decode()
    assert reverse("admin:userprofile_userprofile_import") in changelist
    assert reverse("admin:userprofile_userprofile_export") in changelist

    history = admin_client.get(reverse("admin:userprofile_userprofile_history", args=[profile.pk]))
    assert history.status_code == 200
    assert profile.history.count() == 2  # created, then renamed


def test_task_queue_admin(admin_client):
    assert admin_client.get(reverse("admin:django_q_success_changelist")).status_code == 200
