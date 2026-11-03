from django.urls import include, path

from authentication import views

urlpatterns = [
    # allauth itself. Provider callback URLs (register these with Google/Microsoft):
    #   /api/allauth/google/login/callback/
    #   /api/allauth/microsoft/login/callback/
    path("", include("allauth.urls")),
    # Where a social login or connect ends up (they hand the JWT to the frontend)
    path("social/login/callback", views.social_callback, {"outcome": "social-login-callback"}, name="social-login-callback"),
    path("social/first-login/callback", views.social_callback, {"outcome": "social-first-login-callback"}, name="social-first-login-callback"),
    path("social/connect/callback", views.social_callback, {"outcome": "social-connect-callback"}, name="social-connect-callback"),
    # Error pages the adapter redirects to; the URL name is also the reason
    *[
        path(f"social/exceptions/{reason}", views.social_exception, {"reason": reason}, name=reason)
        for reason in views.SOCIAL_EXCEPTIONS
    ],
    # API
    path("social/accounts", views.SocialAccountListView.as_view(), name="social-account-list"),
    path("logout", views.LogoutView.as_view(), name="auth-logout"),
]
