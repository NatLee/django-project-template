"""With DEBUG off the settings must be safe by default and refuse to start without a secret key."""

import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

PRINT_SETTINGS = (
    "import django; django.setup(); from django.conf import settings as s; "
    "print(s.DEBUG, s.ALLOWED_HOSTS, s.SESSION_COOKIE_SECURE, s.CORS_ALLOW_ALL_ORIGINS, "
    "'debug_toolbar' in s.INSTALLED_APPS)"
)


def run(code_or_args, **env_overrides):
    env = {**os.environ, "DJANGO_SETTINGS_MODULE": "backend.settings", **env_overrides}
    for key, value in env_overrides.items():
        if value is None:
            env.pop(key)
    args = [sys.executable, "-c", code_or_args] if isinstance(code_or_args, str) else [sys.executable, *code_or_args]
    return subprocess.run(args, cwd=BACKEND_DIR, env=env, capture_output=True, text=True, timeout=120)


def test_production_requires_secret_key():
    result = run(PRINT_SETTINGS, DEBUG="false", SECRET_KEY=None)
    assert result.returncode != 0
    assert "SECRET_KEY is required" in result.stderr


def test_production_defaults_are_locked_down():
    result = run(PRINT_SETTINGS, DEBUG="false", SECRET_KEY="x" * 50, ALLOWED_HOSTS=None, CORS_ALLOW_ALL_ORIGINS=None)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "False ['localhost', '127.0.0.1'] True False False"


def test_debug_defaults_to_off():
    result = run(PRINT_SETTINGS, DEBUG=None, SECRET_KEY="x" * 50)
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("False ")


def test_deploy_check_has_no_errors():
    result = run(
        ["manage.py", "check", "--deploy", "--fail-level", "ERROR"],
        DEBUG="false",
        SECRET_KEY="a-long-random-production-secret-key-for-the-deploy-check-0123456789",
        ALLOWED_HOSTS="example.com,localhost",
    )
    assert result.returncode == 0, result.stdout + result.stderr
