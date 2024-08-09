from django.urls import path, include
from authentication import views

urlpatterns = [
    # ===================
    # Django Allauth
    # ===================

    # Include Allauth Routes
    path('', include('allauth.urls')),

    # Provide Callback Route is like this:
    # The prefix `/api/allauth/` is defined in global URLs `./backend/backend/urls.py`.
    # > /api/allauth/{provider}/login/callback/
    # For example:
    #       /api/allauth/google/login/callback/
    #       /api/allauth/microsoft/login/callback/
    # ...

    # ===================

    # ===================
    # Custom Callback Route
    # ===================
    # 第三方帳號登入 Callback
    path('social/login/callback', views.social_login_callback, name='social-login-callback'),
    # 第三方帳號連接 Callback
    path('social/connect/callback', views.social_connect_callback, name='social-connect-callback'),

    # ===================
    # Custom Exceptions
    # ===================
    # 重複的 Email
    path('social/exceptions/duplicate-email', views.duplicate_email, name='duplicate-email'),
    # 社交帳號已經被其他帳號連接
    path('social/exceptions/social-account-already-connected-by-other', views.social_account_already_connected_by_other, name='social-account-already-connected-by-other'),
    # 社交帳號已經被自己連接
    path('social/exceptions/social-account-already-connected-by-self', views.social_account_already_connected_by_self, name='social-account-already-connected-by-self'),
    # 匿名用戶嘗試連接社交帳號
    path('social/exceptions/connect-social-account-without-login', views.connect_social_account_without_login, name='connect-social-account-without-login'),
    # 不在白名單的 Email Domain
    path('social/exceptions/invalid-email-domain', views.invalid_email_domain, name='invalid-email-domain'),

    # ===================
    # Custom API
    # ===================
    # 取得社交帳號列表
    path('social/accounts', views.SocialAccountListView.as_view(), name='social-account-list'),
    # Session 登出
    path('logout', views.LogoutView.as_view(), name='auth-logout'),

]
