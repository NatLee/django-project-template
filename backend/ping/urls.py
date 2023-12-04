from ping import views
from django.urls import path

urlpatterns = [
    path("", views.Ping.as_view(), name="ping"),
    path("/job", views.PingJob.as_view(), name="ping-job"),
    path("/progress/<str:task_id>", views.PingJobProgress.as_view(), name="ping-progress"),
]
