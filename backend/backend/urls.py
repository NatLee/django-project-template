from django.contrib import admin
from django.urls import path
from django.urls import include, re_path

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator

from rest_framework.permissions import AllowAny, IsAdminUser

from django.conf import settings

URL_PREFIX = 'api'

# =================
# Unregister Site in admin panel
from django.contrib.sites.models import Site
admin.site.unregister(Site)
# =================

urlpatterns = []

# ============
# Debug Pages
# ============
if settings.DEBUG:
    urlpatterns += [
        # admin
        path(f"{URL_PREFIX}/__hidden_admin/", admin.site.urls),
        # debug dashboard
        path(f"{URL_PREFIX}/__hidden_dev_dashboard", include("dev_dashboard.urls")),
        # example - ping
        path(f"{URL_PREFIX}/ping", include("ping.urls"), name="ping"),
    ]

# ============
# Auth
# ============
urlpatterns += [
    # ============
    # Custom Allauth
    # ============
    path('api/allauth/', include('authentication.urls')),
    # ============
    # Custom Simple JWT
    # ============
    path(f"{URL_PREFIX}/auth/", include("custom_jwt.urls")),
]

# =================
# Custom APP route
# =================
urlpatterns += [
    # ============
    # 代理其他API的路由
    # ============
    path(f"{URL_PREFIX}/{settings.ROUTE_PATH}/", include("api_proxy.urls")),
]


# -------------- START - Swagger View --------------

# Http & Https
class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema

schema_view = get_schema_view(
    openapi.Info(
        title="Backend service API",
        default_version="v1",
        description="API of backend services.",
    ),
    public=True,
    # permission_classes=(AllowAny,),
    permission_classes = (IsAdminUser,), #is_staff才可使用
    generator_class=BothHttpAndHttpsSchemaGenerator,
)
# --------------- END - Swagger View ----------------


urlpatterns += [
    re_path(
        r"^api/__hidden_swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^api/__hidden_swagger",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^api/__hidden_redoc",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]

# add static files support
from django.conf.urls.static import static
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    
    # add debug toolbar
    import debug_toolbar
    urlpatterns += [
        path(f"{URL_PREFIX}/__hidden_debug/", include(debug_toolbar.urls))
    ]

    # add schema graph
    from schema_graph.views import Schema
    urlpatterns += [
        path(f"{URL_PREFIX}/__hidden_schema", Schema.as_view()),
    ]

    # add silk
    urlpatterns += [path(f"{URL_PREFIX}/silk/", include("silk.urls", namespace="silk"))]

admin.autodiscover()
