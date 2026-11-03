from allauth.socialaccount.models import SocialAccount
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

# ---------------------------------------------------------------- popup pages
# The dev dashboard opens social login in a popup. allauth ends the flow on one of
# these pages; they store the result in localStorage and close themselves.

SOCIAL_CALLBACKS = {
    "social-login-callback": ("Signed in", "You are signed in or already registered."),
    "social-first-login-callback": ("Welcome!", "Your account was created and you are signed in."),
    "social-connect-callback": ("Account connected", "The social account is now linked to your user."),
}

SOCIAL_EXCEPTIONS = {
    "duplicate-email": (
        "Sign-in failed: email already in use",
        "Another account already uses this email. Sign in with that account first, then connect this one.",
    ),
    "social-account-already-connected-by-other": (
        "Connect failed: account already in use",
        "This social account is linked to a different user. Use another account or sign in directly.",
    ),
    "social-account-already-connected-by-self": (
        "Already connected",
        "You have already linked this social account.",
    ),
    "connect-social-account-without-login": (
        "Connect failed: not signed in",
        "Sign in with a session first, then connect a social account.",
    ),
    "invalid-email-domain": (
        "Sign-in failed: email domain not allowed",
        "This email domain is not on the allow list (SOCIALACCOUNT_VALID_EMAIL_DOMAINS).",
    ),
}


def _tokens_for(user) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"access_token": str(refresh.access_token), "refresh_token": str(refresh)}


@never_cache
def social_callback(request, outcome: str):
    """Finish a social login or connect.

    Login pages turn the fresh Django session into a JWT pair and hand it to the
    opener through the page itself, so tokens never appear in a URL or a server log.
    """
    title, message = SOCIAL_CALLBACKS[outcome]
    context = {"title": title, "message": message, "success": True, "tokens": None}
    if outcome != "social-connect-callback":
        if request.user.is_authenticated:
            context["tokens"] = _tokens_for(request.user)
        else:
            context.update(title="Not signed in", message="The social login did not finish.", success=False)
    return render(request, "authentication/popup.html", context)


def social_exception(request, reason: str):
    title, message = SOCIAL_EXCEPTIONS[reason]
    return render(
        request, "authentication/popup.html", {"title": title, "message": message, "success": False, "tokens": None}
    )


# ---------------------------------------------------------------- API


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.session.flush()
        return Response({"message": "登出成功"}, status=status.HTTP_200_OK)


class SocialAccountListView(APIView):
    """List the caller's linked social accounts, or unlink one."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        accounts = [
            {
                "id": account.id,
                "provider": account.provider,
                "uid": account.uid,
                "extra_data": account.extra_data,
                "date_joined": account.date_joined,
                "last_login": account.last_login,
            }
            for account in SocialAccount.objects.filter(user=user)
        ]
        return Response(
            {"user_id": user.id, "username": user.username, "email": user.email, "social_accounts": accounts},
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        user = request.user
        account_id = request.data.get("account_id")
        if not account_id:
            return Response({"error": "必須提供 account_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = SocialAccount.objects.get(id=account_id, user=user)
        except (SocialAccount.DoesNotExist, ValueError):
            return Response({"error": "找不到指定的社交帳號或該帳號不屬於當前用戶"}, status=status.HTTP_404_NOT_FOUND)

        # Without a password, the last social account is the only way to sign in.
        if SocialAccount.objects.filter(user=user).count() == 1 and not user.has_usable_password():
            return Response({"error": "無法解除綁定最後一個社交帳號"}, status=status.HTTP_400_BAD_REQUEST)

        account.delete()
        return Response({"message": "社交帳號已成功解綁"}, status=status.HTTP_200_OK)
