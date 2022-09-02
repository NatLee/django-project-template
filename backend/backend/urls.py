from django.contrib import admin
from django.urls import path
from django.urls import include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import AllowAny, IsAdminUser

urlpatterns = [
    re_path(r"__hiddenadmin/", admin.site.urls),
    path("api/auth/", include("custom_jwt.urls"), name="jwt"),
    path("__user/", include("userprofile.urls"), name="userprofile"),
    path("proxy/", include("api_proxy.urls"), name="api_proxy"),
    path("example_api/", include("api.urls"), name="api"),
]


"""
swagger
"""
schema_view = get_schema_view(
    openapi.Info(
        title="BACKEND API",
        default_version="v1",
        description="BACKEND API",
    ),
    public=True,
    permission_classes=(AllowAny,)
    # permission_classes = (IsAdminUser,) #is_staff才可使用
)

urlpatterns += [
    re_path(
        r"^__hiddenswagger(?P<format>\.json|\.yaml)$",
        login_required(schema_view.without_ui(cache_timeout=0)),
        name="schema-json",
    ),
    re_path(
        r"^__hiddenswagger$",
        login_required(schema_view.with_ui("swagger", cache_timeout=0)),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$",
        login_required(schema_view.with_ui("redoc", cache_timeout=0)),
        name="schema-redoc",
    ),
    re_path(r"^accounts/", include("rest_framework.urls",
            namespace="rest_framework")),
]
