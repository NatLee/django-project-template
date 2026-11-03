"""Health check used by Docker Compose, CI and any load balancer in front of the app."""

import logging
import uuid

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

logger = logging.getLogger("django")


def _database() -> None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")


def _cache() -> None:
    key = f"health:{uuid.uuid4().hex}"
    cache.set(key, "ok", timeout=5)
    if cache.get(key) != "ok":
        raise RuntimeError("cache did not return the value it just stored")
    cache.delete(key)


CHECKS = {"database": _database, "cache": _cache}


@never_cache
@require_GET
def health(request):
    """Return 200 when PostgreSQL and Redis answer, 503 otherwise."""
    results = {}
    for name, check in CHECKS.items():
        try:
            check()
            results[name] = "ok"
        except Exception:  # report any failure as "error" without leaking details
            logger.exception("Health check %s failed", name)
            results[name] = "error"
    healthy = all(value == "ok" for value in results.values())
    return JsonResponse({"status": "ok" if healthy else "error", "checks": results}, status=200 if healthy else 503)
