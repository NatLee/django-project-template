"""Login history: every login is recorded; the location is filled in by a background task."""

from datetime import timedelta

import pytest
import requests
from django.contrib.auth import login
from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory
from django.utils import timezone

from django_login_history import tasks
from django_login_history.models import Login
from django_login_history.utils.get_client_ip import get_client_ip

pytestmark = pytest.mark.django_db


class FakeGeo:
    def raise_for_status(self):
        pass

    def json(self):
        return {"status": "success", "country": "Taiwan", "regionName": "Taipei City", "city": "Taipei"}


def log_in(user):
    """Log in through a real request object (REMOTE_ADDR 127.0.0.1), like a login view does."""
    request = RequestFactory().get("/", HTTP_USER_AGENT="pytest")
    request.session = SessionStore()
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")


def test_login_is_recorded(user):
    log_in(user)
    record = Login.objects.get(user=user)
    assert record.ip == "127.0.0.1"
    assert record.user_agent == "pytest"
    assert record.country == ""  # the lookup is switched off in the test settings


def test_location_is_filled_in_the_background(user, settings, monkeypatch):
    settings.LOGIN_HISTORY_GEOIP_URL = "http://geo.test/json/{ip}"
    asked = []

    def fake_get(url, timeout):
        asked.append(url)
        return FakeGeo()

    monkeypatch.setattr(requests, "get", fake_get)

    log_in(user)

    record = Login.objects.get(user=user)
    assert asked == ["http://geo.test/json/127.0.0.1"]
    assert (record.country, record.region, record.city) == ("Taiwan", "Taipei City", "Taipei")


def test_failed_lookup_leaves_the_record_alone(user, settings, monkeypatch):
    settings.LOGIN_HISTORY_GEOIP_URL = "http://geo.test/json/{ip}"

    def down(url, timeout):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(requests, "get", down)
    record = Login.objects.create(user=user, ip="8.8.8.8", user_agent="test")
    assert tasks.fill_location(record.pk) == {}
    record.refresh_from_db()
    assert record.country == ""


def test_client_ip_prefers_the_first_public_forwarded_address():
    request = RequestFactory().get("/", HTTP_X_FORWARDED_FOR="10.0.0.5, 203.0.113.9", REMOTE_ADDR="172.18.0.4")
    assert get_client_ip(request) == "203.0.113.9"


def test_client_ip_ignores_private_networks():
    request = RequestFactory().get("/", REMOTE_ADDR="192.168.1.20")
    assert get_client_ip(request) is None


def test_chart_data_has_one_row_per_user_per_day(user, other_user):
    Login.objects.create(user=user, ip="8.8.8.8", user_agent="test")
    today = timezone.localdate()
    rows = Login.get_all_users_login_count_by_date_range((today - timedelta(days=1)).isoformat(), today.isoformat())
    assert len(rows) == 2 * 2  # two users, two days
    alice_today = next(r for r in rows if r["id"] == user.pk and r["date"] == today.isoformat())
    assert alice_today["count"] == 1


def test_chart_data_rejects_bad_dates():
    with pytest.raises(ValueError):
        Login.get_all_users_login_count_by_date_range("yesterday", "today")


def test_cleanup_removes_only_old_records(user, settings):
    settings.LOGIN_HISTORY_RETENTION_DAYS = 30
    old = Login.objects.create(user=user, ip="8.8.8.8", user_agent="test")
    Login.objects.filter(pk=old.pk).update(date=timezone.now() - timedelta(days=31))
    Login.objects.create(user=user, ip="8.8.8.8", user_agent="test")
    assert tasks.cleanup_old_records() == 1
    assert Login.objects.count() == 1
