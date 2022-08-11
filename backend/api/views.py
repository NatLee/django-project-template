from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from common.decorators import KeyCheck
from common.helperfunc import api_response
from common import errorcode

key_check_ = KeyCheck(SystemName="api")


class Test(APIView):
    permission_classes = (AllowAny,)

    required_data = ["name"]

    @key_check_.key_check(required_data)
    @swagger_auto_schema(
        operation_summary="GET",
        operation_description="",
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
        manual_parameters=[
            openapi.Parameter(
                name="name",
                in_=openapi.IN_QUERY,
                description="Name",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
    )
    def get(self, request, input_data, router):
        """
        param:
            必填欄位：
                name
            非必填欄位：
                -
        """
        ret = {"Message": "Success", "Data": input_data["name"]}
        return api_response(ret)

    required_data = ["name"]

    @key_check_.key_check(required_data)
    @swagger_auto_schema(
        operation_summary="POST",
        operation_description="",
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
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="Name")
            },
        ),
    )
    def post(self, request, input_data, router):
        """
        param:
            必填欄位：
                name
            非必填欄位：
                -
        """
        ret = {"Message": "Success", "Data": input_data["name"]}
        return api_response(ret)

    required_data = ["name"]

    @key_check_.key_check(required_data)
    @swagger_auto_schema(
        operation_summary="PUT",
        operation_description="",
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
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="Name")
            },
        ),
    )
    def put(self, request, input_data, router):
        """
        param:
            必填欄位：
                name
            非必填欄位：
                -
        """
        ret = {"Message": "Success", "Data": input_data["name"]}
        return api_response(ret)

    required_data = ["name"]

    @key_check_.key_check(required_data)
    @swagger_auto_schema(
        operation_summary="PATCH",
        operation_description="",
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
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="Name")
            },
        ),
    )
    def patch(self, request, input_data, router):
        """
        param:
            必填欄位：
                name
            非必填欄位：
                -
        """
        ret = {"Message": "Success", "Data": input_data["name"]}
        return api_response(ret)

    required_data = ["name"]

    @key_check_.key_check(required_data)
    @swagger_auto_schema(
        operation_summary="DELETE",
        operation_description="",
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
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="Name")
            },
        ),
    )
    def delete(self, request, input_data, router):
        """
        param:
            必填欄位：
                name
            非必填欄位：
                -
        """
        ret = {"Message": "Success", "Data": input_data["name"]}
        return api_response(ret)
