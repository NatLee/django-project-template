from django.urls import path
from api_proxy import views

urlpatterns = [
    path("", views.APIProxy.as_view(), {"resource": ""}),
    path("<path:resource>", views.APIProxy.as_view()),
]
