from django.contrib import admin
from django.urls import path
from django.urls import include, re_path

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator

from rest_framework.permissions import AllowAny, IsAdminUser

from rest_framework.routers import DefaultRouter
from djoser import views as djoser_views

from django.conf import settings

router = DefaultRouter(trailing_slash=False)
router.register("users", djoser_views.UserViewSet)

URL_PREFIX = 'api'


urlpatterns = []

# pages
if settings.DEBUG:
    urlpatterns += [
        # admin
        path(f"{URL_PREFIX}/__hidden_admin/", admin.site.urls),
        # debug dashboard
        path(f"{URL_PREFIX}/__hidden_dev_dashboard", include("dev_dashboard.urls")),
        # example - ping
        path(f"{URL_PREFIX}/ping", include("ping.urls"), name="ping"),
    ]

# Auth
urlpatterns += [
    # 3rd party jwt
    path(f"{settings.JWT_3RD_PREFIX}/", include("django_simple_third_party_jwt.urls")),
    # auth
    path(f"{URL_PREFIX}/auth/", include("custom_jwt.urls")),
]


# Custom APP route
urlpatterns += [
    # index
    path(f"{URL_PREFIX}/", include(router.urls), name="api"),
    # proxy
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
