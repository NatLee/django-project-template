from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.shortcuts import redirect, render


def social_providers() -> list[dict]:
    """Every provider the template supports, with its client ID when .env sets one."""
    configured = settings.SOCIALACCOUNT_PROVIDERS
    return [
        {
            "id": provider,
            "name": provider.title(),
            "client_id": configured[provider]["APPS"][0]["client_id"] if provider in configured else "",
        }
        for provider in settings.SOCIAL_PROVIDER_SETTINGS
    ]


def dashboard(request):
    providers = social_providers()
    return render(
        request,
        "dev_dashboard/dashboard.html",
        {"providers": providers, "configured_providers": [p for p in providers if p["client_id"]]},
    )


def login(request):
    """Session login for the playground. The same form can also ask for a JWT (see login.js)."""
    error = None
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        if user is not None:
            auth_login(request, user)
            return redirect("dev-dashboard")
        error = "Wrong username or password."
    return render(request, "dev_dashboard/login.html", {"error": error})


def logout(request):
    request.session.flush()
    return redirect("dev-dashboard")
