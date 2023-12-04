from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import django_rq

from ping.task import ping_job

from common.helperfunc import api_response
from common.cache_deco import CacheDeco

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
        return api_response(ret)

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
        job = ping_job.delay(msg="pong")
        ret = {"status": "ok", "response": job.id, "detail": "Good job! ;)"}
        return api_response(ret)


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
        queue = django_rq.get_queue('default')
        job = queue.fetch_job(task_id)

        if job.is_finished:
            state = 'FINISHED'
            details = job.result
        elif job.is_queued:
            state = 'QUEUED'
        elif job.is_started:
            state = 'STARTED'
        elif job.is_failed:
            state = 'FAILED'
            details = str(job.exc_info)
        else:
            state = 'UNKNOWN'

        response_data = {
            'state': state,
            'details': details
        }
        return api_response(response_data)