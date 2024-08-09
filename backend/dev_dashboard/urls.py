from django.urls import path

from dev_dashboard import views

urlpatterns = [
    path("", views.dashboard, name="dev-dashboard"),
    path("/login", views.login, name="dev-login"),
    path("/logout", views.logout, name="dev-session-logout"),
]
