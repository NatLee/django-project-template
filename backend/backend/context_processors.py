from django.conf import settings


def project(request):
    """Expose the project name (from PROJECT_NAME in .env) to every template."""
    return {"PROJECT_NAME": settings.PROJECT_NAME}
