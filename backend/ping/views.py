from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.response import Response

from django_q.tasks import async_task, fetch
from ping.task import ping_job

from common.cache_deco import CacheDeco


def PingIndex(request):
    # ping template path
    return render(request, "index.html")

class Ping(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_summary="GET",
        operation_description="Ping!",
        responses={
            "200": openapi.Response(
                description="message",
                examples={
                    "application/json": {
                        "result": [{"Message": "Success", "Data": "<name>"}],
                        "code": 0,
                    }
                },
            )
        },
    )
    @CacheDeco()
    def get(self, request):
        """
        Ping!
        """
        ret = {"status": "ok", "response": "pong", "detail": "you got it! ;)"}
        return Response(ret)


# ================== RQ ==================

class PingJob(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_summary="GET",
        operation_description="Ping!",
        responses={
            "200": openapi.Response(
                description="message job using RQ",
                examples={
                    "application/json": {
                        "result": [{"Message": "Success", "Data": "<name>"}],
                        "code": 0,
                    }
                },
            )
        },
    )
    def get(self, request):
        """
        Ping by using django-rq!
        """
        task_id = async_task(
            ping_job,
            msg="pong",
            sync=True,
        )
        ret = {"status": "ok", "response": task_id, "detail": "Good job! ;)"}
        return Response(ret)

class PingJobProgress(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_summary="GET",
        operation_description="Check ping progress!",
        responses={
            "200": openapi.Response(
                description="Check progress of job",
                examples={
                    "application/json": {
                        "result": [{"Message": "Success", "Data": "<name>"}],
                        "code": 0,
                    }
                },
            )
        },
    )
    def get(self, request, task_id):
        """
        Check progress of job
        """

        task = fetch(task_id)
        if not task.success:
            state = 'PENDING'
            details = 'Task is still pending'
        else:
            state = 'SUCCESS'
            details = task.result

        response_data = {
            'state': state,
            'details': details
        }
        return Response(response_data)
    
# ===============================================



