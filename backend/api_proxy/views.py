import json
import traceback
import time
import re
from urllib.parse import urlparse
from loguru import logger
import requests

# Create your views here.

from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from django.conf import settings


class APIProxy(APIView):
    """API proxy."""

    authentication_classes = [
        SessionAuthentication,
        JWTAuthentication,
    ]
    permission_classes = [IsAuthenticated]

    def parse_path(self, request):
        parsed_path = urlparse(request.get_full_path())
        path = parsed_path.path.rstrip("/")
        path = re.sub("/proxy", "api", path, 1)
        return path

    def response(self, resp: dict):
        return JsonResponse(resp, safe=False, json_dumps_params={"ensure_ascii": False})

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Get."""
        try:

            params = dict(request.GET)
            path = self.parse_path(request)

            username = request.user.username
            displayname = request.user.userprofile.displayname
            realname = request.user.userprofile.realname

            logger.debug(f"{username}::{displayname}::{path}")
            params.update(
                {
                    "username": f"{username}",
                    "realname": f"{realname}",
                }
            )
            logger.debug(params)
            resp = requests.get(
                f"{settings.API_URL}{path}",
                params=params,
                timeout=180,
                verify=False,
            )
            logger.debug(
                f"{username}::{resp.url}::{resp.status_code} {params}")
            return self.response(resp.json())

        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())

        return self.response({"status": "error"})

    def post(self, request, *args, **kwargs):
        """Post."""
        try:
            params = request.json
            logger.debug(f"check params: {params}")
            path = self.parse_path(request)

            username = request.user.username
            displayname = request.user.userprofile.displayname
            realname = request.user.userprofile.realname

            params.update(
                {
                    "username": username,
                    "realname": realname,
                    "displayname": displayname
                }
            )
            for t in range(0, 5):
                start = time.time()
                resp = requests.post(
                    f"{settings.API_URL}{path}",
                    data=json.dumps(params),
                    headers={
                        "version": settings.API_VERSION,
                    },
                    verify=False,
                )
                # total is not ok, but do not retry request which response time is too long
                end = time.time()
                total_time = end - start
                if total_time > 15:
                    break
                logger.error(f"function: {resp.url} retry: {t+1}/{5}")

            logger.debug(
                f"{username}::{resp.url}::{resp.status_code} {params}")
            return self.response(resp.json())

        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
        return self.response({"status": "error"})
