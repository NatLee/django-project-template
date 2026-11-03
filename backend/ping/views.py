from django.shortcuts import render
from django_q.tasks import async_task, fetch
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.cache_deco import CacheDeco


def PingIndex(request):
    """Page that tries the websocket and the background task queue."""
    return render(request, "ping/index.html")


class Ping(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_summary="Ping",
        responses={
            "200": openapi.Response(
                description="The server is up",
                examples={"application/json": {"status": "ok", "response": "pong", "detail": "you got it! ;)"}},
            )
        },
    )
    @CacheDeco()
    def get(self, request):
        return Response({"status": "ok", "response": "pong", "detail": "you got it! ;)"})


class PingJob(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_summary="Queue a background task",
        operation_description="Queues `ping.task.ping_job`; the django-q2 worker runs it. Poll the progress endpoint with the returned id.",
        responses={
            "200": openapi.Response(
                description="Task id",
                examples={"application/json": {"status": "ok", "response": "<task id>", "detail": "Good job! ;)"}},
            )
        },
    )
    def get(self, request):
        task_id = async_task("ping.task.ping_job", msg="pong")
        return Response({"status": "ok", "response": task_id, "detail": "Good job! ;)"})


class PingJobProgress(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_summary="Check a background task",
        responses={
            "200": openapi.Response(
                description="PENDING until the worker finishes, then SUCCESS (with the result) or FAILURE (with the error)",
                examples={"application/json": {"state": "SUCCESS", "details": "pong"}},
            )
        },
    )
    def get(self, request, task_id):
        task = fetch(task_id)
        if task is None:  # not picked up or not finished yet
            return Response({"state": "PENDING", "details": "Task is still pending"})
        return Response({"state": "SUCCESS" if task.success else "FAILURE", "details": task.result})
