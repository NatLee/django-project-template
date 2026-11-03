from io import StringIO

from django.core.management import call_command


def test_no_missing_migrations(db):
    """Model changes must ship with their migration files (they are committed now)."""
    output = StringIO()
    call_command("makemigrations", "--check", "--dry-run", stdout=output)
    assert "No changes detected" in output.getvalue()
