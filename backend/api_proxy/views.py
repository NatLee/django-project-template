import json
import re
from urllib.parse import urlparse
import requests

# Create your views here.

from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from django.http import JsonResponse
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

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

    route_path = settings.ROUTE_PATH
    target_path = settings.TARGET_PATH

    def parse_path(self, request):
        parsed_path = urlparse(request.get_full_path())
        path = parsed_path.path.rstrip("/")
        path = re.sub(f'/{self.route_path}', self.target_path, path, 1)
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

    def post_request(self, request, method):
        logger.debug(f"----- Proxy {method}")
        response = {"status": "error"}
        with logger.catch():
            params = json.loads(request.body)
            logger.debug(f"JSON Params: {params}")
            path = self.get_proxy_path(request)
            params = self.update_payload(request, params)
            middle_resp_ = self.send_request(method, path, json=params)
            response = middle_resp_.json()
        return response

    def post(self, request, *args, **kwargs):
        """Post."""
        response = self.post_request(request, method='POST')
        return self.response(response)

    def patch(self, request, *args, **kwargs):
        """Patch."""
        response = self.post_request(request, method='PATCH')
        return self.response(response)

    def delete(self, request, *args, **kwargs):
        """Delete"""
        response = self.post_request(request, method='DELETE')
        return self.response(response)

    def put(self, request, *args, **kwargs):
        """Put"""
        response = self.post_request(request, method='PUT')
        return self.response(response)
