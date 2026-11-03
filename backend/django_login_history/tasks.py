"""Background tasks for the login history (run by the django-q2 worker)."""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def lookup_location(ip: str) -> dict:
    """Ask LOGIN_HISTORY_GEOIP_URL (ip-api.com by default) where an IP address is."""
    url = settings.LOGIN_HISTORY_GEOIP_URL.format(ip=ip)
    try:
        response = requests.get(url, timeout=settings.LOGIN_HISTORY_GEOIP_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.error("Location lookup for %s failed: %s", ip, exc)
        return {}
    if data.get("status") != "success":
        logger.warning("Location lookup for %s returned %s", ip, data.get("status"))
        return {}
    return {"country": data.get("country", ""), "region": data.get("regionName", ""), "city": data.get("city", "")}


def fill_location(login_id: int) -> dict:
    """Store the country, region and city of a login's IP address."""
    from django_login_history.models import Login

    login = Login.objects.filter(pk=login_id).first()
    if login is None or not login.ip:
        return {}
    location = lookup_location(login.ip)
    if location:
        Login.objects.filter(pk=login_id).update(**location)
    return location


def cleanup_old_records() -> int:
    """Delete login records older than LOGIN_HISTORY_RETENTION_DAYS. Schedule it in the admin (Django Q > Scheduled tasks)."""
    from django_login_history.models import Login

    return Login.cleanup_old_records()
