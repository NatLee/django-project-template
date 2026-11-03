"""JWT endpoints that answer with `access_token` / `refresh_token` keys (plus the username on login)."""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# SimpleJWT key -> key this API returns
RENAMED_KEYS = {"access": "access_token", "refresh": "refresh_token"}


def rename_token_keys(data: dict) -> dict:
    return {RENAMED_KEYS.get(key, key): value for key, value in data.items()}


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = rename_token_keys(super().validate(attrs))
        data["username"] = self.user.username
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        return rename_token_keys(super().validate(attrs))


class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer
