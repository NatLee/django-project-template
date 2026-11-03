"""Forward authenticated requests to another API.

`/api/proxy/<resource>` is sent to `{API_URL}{TARGET_PATH}/<resource>` with the
same method, query string and JSON body. The caller's username, real name and
display name are added to the parameters, so the other service knows who asked.
"""

import logging
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)


class APIProxy(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def target_url(self, resource: str) -> str:
        return urljoin(settings.API_URL, f"{settings.TARGET_PATH}/{resource}".rstrip("/"))

    def user_info(self, request) -> dict:
        profile = getattr(request.user, "userprofile", None)
        return {
            "username": request.user.username,
            "realname": request.user.get_full_name(),
            "displayname": getattr(profile, "displayname", ""),
        }

    def forward(self, request, resource: str):
        if not settings.API_URL:
            return self.error("API_URL is not configured", status=503)

        url = self.target_url(resource)
        if request.method == "GET":
            payload = {"params": {**dict(request.GET), **self.user_info(request)}}
        else:
            body = request.data if isinstance(request.data, dict) else {}
            payload = {"json": {**body, **self.user_info(request)}}
        logger.debug("Proxy %s %s", request.method, url)

        try:
            upstream = requests.request(
                request.method,
                url,
                headers={"version": settings.API_VERSION},
                timeout=settings.API_PROXY_TIMEOUT,
                verify=settings.API_PROXY_VERIFY_TLS,
                **payload,
            )
            upstream.raise_for_status()
            data = upstream.json()
        except (requests.RequestException, ValueError) as exc:
            logger.error("Proxy %s %s failed: %s", request.method, url, exc)
            return self.error(str(exc), status=502)
        return JsonResponse(data, safe=False, status=upstream.status_code, json_dumps_params={"ensure_ascii": False})

    @staticmethod
    def error(message: str, status: int) -> JsonResponse:
        return JsonResponse({"status": "error", "message": message}, status=status)

    def get(self, request, resource=""):
        return self.forward(request, resource)

    def post(self, request, resource=""):
        return self.forward(request, resource)

    def put(self, request, resource=""):
        return self.forward(request, resource)

    def patch(self, request, resource=""):
        return self.forward(request, resource)

    def delete(self, request, resource=""):
        return self.forward(request, resource)
