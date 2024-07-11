import json
import re
from urllib.parse import urlparse
import requests

# 引入所需的模組

from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from django.http import JsonResponse
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

class APIProxy(APIView):
    """API 代理類別"""

    # 設定身份驗證類別
    authentication_classes = [
        SessionAuthentication,
        JWTAuthentication,
    ]
    # 設定權限類別
    permission_classes = [IsAuthenticated]

    # 設定請求標頭
    headers = {
        "version": settings.API_VERSION,
    }

    # 從設定檔中取得路由路徑與目標路徑
    route_path = settings.ROUTE_PATH
    target_path = settings.TARGET_PATH

    def parse_path(self, request):
        # 解析請求的完整路徑
        parsed_path = urlparse(request.get_full_path())
        path = parsed_path.path.rstrip("/")
        # 將路徑中的 route_path 替換為 target_path
        path = re.sub(f'/{self.route_path}', self.target_path, path, 1)
        return path

    def get_proxy_path(self, request):
        # 取得代理的完整 URL 路徑
        path = self.parse_path(request)
        logger.debug(f"URL: {path}")
        return f"{settings.API_URL}{path}"

    def response(self, resp: dict):
        # 回傳 JSON 格式的回應
        return JsonResponse(resp, safe=False, json_dumps_params={"ensure_ascii": False})

    def update_payload(self, request, params):
        # 更新請求的參數，加入使用者資訊
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
        # 發送 HTTP 請求
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=self.headers,
                timeout=timeout,
                verify=verify,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"status": "error", "message": str(e)}
        return response

    def dispatch(self, request, *args, **kwargs):
        # 分發請求
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """處理 GET 請求"""
        logger.debug("----- Proxy GET")
        response = {"status": "error"}
        with logger.catch():
            params = dict(request.GET)
            path = self.get_proxy_path(request)
            params = self.update_payload(request, params)
            middle_resp_ = self.send_request("GET", path, params=params)
            if isinstance(middle_resp_, dict):
                response = middle_resp_
            else:
                response = middle_resp_.json()
        return self.response(response)

    def post_request(self, request, method):
        # 處理 POST、PATCH、DELETE、PUT 請求
        logger.debug(f"----- Proxy {method}")
        response = {"status": "error"}
        with logger.catch():
            params = json.loads(request.body)
            logger.debug(f"JSON Params: {params}")
            path = self.get_proxy_path(request)
            params = self.update_payload(request, params)
            middle_resp_ = self.send_request(method, path, json=params)
            if isinstance(middle_resp_, dict):
                response = middle_resp_
            else:
                response = middle_resp_.json()
        return response

    def post(self, request, *args, **kwargs):
        """處理 POST 請求"""
        response = self.post_request(request, method='POST')
        return self.response(response)

    def patch(self, request, *args, **kwargs):
        """處理 PATCH 請求"""
        response = self.post_request(request, method='PATCH')
        return self.response(response)

    def delete(self, request, *args, **kwargs):
        """處理 DELETE 請求"""
        response = self.post_request(request, method='DELETE')
        return self.response(response)

    def put(self, request, *args, **kwargs):
        """處理 PUT 請求"""
        response = self.post_request(request, method='PUT')
        return self.response(response)
