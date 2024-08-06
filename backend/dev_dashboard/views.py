from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from dev_dashboard.forms import UserRegistrationForm
import logging

logger = logging.getLogger(__name__)

def dashboard(request):
    # template path
    return render(
        request,
        "dashboard/dashboard.html",
        {
            'social_google_client_id':settings.SOCIAL_GOOGLE_CLIENT_ID,
            'social_microsoft_client_id':settings.SOCIAL_MICROSOFT_CLIENT_ID,
        }
    )


def register(request):
    user_form = UserRegistrationForm()
    # template path
    return render(request, "dashboard/register.html", {"user_form": user_form})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Session 登入
            auth_login(request, user)
            return redirect('dev-dashboard')

    return render(request, "dashboard/login.html")

@csrf_exempt
def logout(request):
    request.session.flush()
    return redirect('dev-dashboard')
