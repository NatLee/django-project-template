from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sites.models import Site
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework.permissions import IsAdminUser

from backend.health import health

# NGINX forwards everything under /api to Django (see nginx/default.conf).
URL_PREFIX = "api"

# The admin shows the project name from .env instead of "Django administration".
admin.site.site_header = admin.site.site_title = f"{settings.PROJECT_NAME} admin"
# allauth needs the Sites framework, but nobody needs to edit it in the admin.
admin.site.unregister(Site)

urlpatterns = [
    path(f"{URL_PREFIX}/health", health, name="health"),
    # Social login (allauth) plus our JWT hand-off pages
    path(f"{URL_PREFIX}/allauth/", include("authentication.urls")),
    # JWT endpoints
    path(f"{URL_PREFIX}/auth/", include("custom_jwt.urls")),
    # Forward requests to another API
    path(f"{URL_PREFIX}/{settings.ROUTE_PATH}/", include("api_proxy.urls")),
]

# Development pages: admin, login playground and the websocket / task examples.
if settings.DEBUG:
    urlpatterns += [
        path(f"{URL_PREFIX}/__hidden_admin/", admin.site.urls),
        path(f"{URL_PREFIX}/__hidden_dev_dashboard", include("dev_dashboard.urls")),
        path(f"{URL_PREFIX}/ping", include("ping.urls")),
    ]


class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    """List both schemes so "Try it out" works behind HTTP and HTTPS proxies."""

    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title=f"{settings.PROJECT_NAME} API",
        default_version="v1",
        description=f"API of {settings.PROJECT_NAME}.",
    ),
    public=True,
    permission_classes=(IsAdminUser,),  # staff only
    generator_class=BothHttpAndHttpsSchemaGenerator,
)

urlpatterns += [
    re_path(
        rf"^{URL_PREFIX}/__hidden_swagger\.(?P<format>json|yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(rf"^{URL_PREFIX}/__hidden_swagger", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    re_path(rf"^{URL_PREFIX}/__hidden_redoc", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

# Static files in development (WhiteNoise serves them when DEBUG is off).
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Debug tools, mounted only when settings.py installed them (DEBUG on).
if apps.is_installed("debug_toolbar"):
    urlpatterns += [path(f"{URL_PREFIX}/__hidden_debug/", include("debug_toolbar.urls"))]
if apps.is_installed("schema_graph"):
    from schema_graph.views import Schema

    urlpatterns += [path(f"{URL_PREFIX}/__hidden_schema", Schema.as_view(), name="schema-graph")]
if apps.is_installed("silk"):
    urlpatterns += [path(f"{URL_PREFIX}/silk/", include("silk.urls", namespace="silk"))]
