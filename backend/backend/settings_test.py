"""Settings for pytest: the normal settings plus a few test-only tweaks."""

from backend.settings import *  # noqa: F403
from backend.settings import INSTALLED_APPS, MIDDLEWARE, Q_CLUSTER

# The debug toolbar refuses to run under a test runner.
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]
MIDDLEWARE = [m for m in MIDDLEWARE if not m.startswith("debug_toolbar.")]

# Run background tasks inline so tests can read their result right away.
# The end-to-end tests in CI cover the real worker.
Q_CLUSTER = {**Q_CLUSTER, "sync": True}

# Fast password hashing; never call external services from tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
LOGIN_HISTORY_GEOIP_URL = ""
