import json
import re
from urllib.parse import urlparse
from loguru import logger
import requests

# Create your views here.

from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from django.http import JsonResponse
from django.conf import settings


class APIProxy(APIView):
    """API proxy."""

    authentication_classes = [
        SessionAuthentication,
        JWTAuthentication,
    ]
    permission_classes = [IsAuthenticated]

    headers = {
        "version": settings.API_VERSION,
    }

    route_path = "/proxy"
    target_path = "api"

    def parse_path(self, request):
        parsed_path = urlparse(request.get_full_path())
        path = parsed_path.path.rstrip("/")
        path = re.sub(self.route_path, self.target_path, path, 1)
        return path

    def get_proxy_path(self, request):
        path = self.parse_path(request)
        logger.debug(f"URL: {path}")
        return f"{settings.API_URL}{path}"

    def response(self, resp: dict):
        return JsonResponse(resp, safe=False, json_dumps_params={"ensure_ascii": False})

    def update_payload(self, request, params):
        username = request.user.username
        displayname = request.user.userprofile.displayname
        realname = request.user.userprofile.realname
        logger.debug(f"Username: {username}")
        params.update(
            {"username": username, "realname": realname, "displayname": displayname}
        )
        return params

    def send_request(
        self, method, url, params=None, data=None, json=None, timeout=180, verify=False
    ):
        return requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=self.headers,
            timeout=timeout,
            verify=verify,
        )

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Get."""
        logger.debug("----- Proxy GET")
        response = {"status": "error"}
        with logger.catch():
            params = dict(request.GET)
            path = self.get_proxy_path(request)
            params = self.update_payload(request, params)
            middle_resp_ = self.send_request("GET", path, params=params)
            response = middle_resp_.json()
        return self.response(response)

    def post(self, request, *args, **kwargs):
        """Post."""
        logger.debug("----- Proxy POST")
        response = {"status": "error"}
        with logger.catch():
            params = json.loads(request.body)
            logger.debug(f"JSON Params: {params}")
            path = self.get_proxy_path(request)
            params = self.update_payload(request, params)
            middle_resp_ = self.send_request("POST", path, json=params)
            response = middle_resp_.json()
        return self.response(response)

    def patch(self, request, *args, **kwargs):
        """Patch."""
        logger.debug("----- Proxy PATCH")
        response = {"status": "error"}
        with logger.catch():
            params = json.loads(request.body)
            logger.debug(f"JSON Params: {params}")
            path = self.get_proxy_path(request)
            params = self.update_payload(request, params)
            middle_resp_ = self.send_request("PATCH", path, json=params)
            response = middle_resp_.json()
        return self.response(response)

    def delete(self, request, *args, **kwargs):
        """Delete"""
        logger.debug("----- Proxy DELETE")
        response = {"status": "error"}
        with logger.catch():
            params = json.loads(request.body)
            logger.debug(f"JSON Params: {params}")
            path = self.get_proxy_path(request)
            params = self.update_payload(request, params)
            middle_resp_ = self.send_request("DELETE", path, json=params)
            response = middle_resp_.json()
        return self.response(response)

    def put(self, request, *args, **kwargs):
        """Put"""
        logger.debug("----- Proxy PUT")
        response = {"status": "error"}
        with logger.catch():
            params = json.loads(request.body)
            logger.debug(f"JSON Params: {params}")
            path = self.get_proxy_path(request)
            params = self.update_payload(request, params)
            middle_resp_ = self.send_request("PUT", path, json=params)
            response = middle_resp_.json()
        return self.response(response)
