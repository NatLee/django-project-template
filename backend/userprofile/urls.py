from django.urls import path
from userprofile import views

urlpatterns = [
    path("register", views.register, name="register"),
    path("profile", views.profile, name="profile"),
]
