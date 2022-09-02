from django.shortcuts import render, redirect

# Create your views here.

from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Your account has been created! You are now able to log in"
            )
            return redirect("__hiddenadmin")
    else:
        form = UserRegisterForm()
    return render(request, "userprofile/accounts/register.html", {"form": form})


def dashboard(request):
    return render(request, "userprofile/accounts/dashboard.html", {})


class MyLoginView(LoginView):
    template_name = 'userprofile/registration/login.html'
