from django.shortcuts import render

def social_login_callback(request):
    return render(request, 'social_login_callback.html')

def social_connect_callback(request):
    return render(request, 'social_connect_callback.html')

def social_first_login_callback(request):
    return render(request, 'social_first_login_callback.html')

def duplicate_email(request):
    return render(request, 'exceptions/duplicate_email.html')

def social_account_already_connected_by_other(request):
    return render(request, 'exceptions/social_account_already_connected_by_other.html')

def social_account_already_connected_by_self(request):
    return render(request, 'exceptions/social_account_already_connected_by_self.html')

def connect_social_account_without_login(request):
    return render(request, 'exceptions/connect_social_account_without_login.html')

def invalid_email_domain(request):
    return render(request, 'exceptions/invalid_email_domain.html')

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from allauth.socialaccount.models import SocialAccount

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.session.flush()
        return Response({'message': '登出成功'}, status=status.HTTP_200_OK)

class SocialAccountListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        social_accounts = SocialAccount.objects.filter(user=user)
        
        social_account_list = []
        for account in social_accounts:
            social_account_list.append({
                'id': account.id,
                'provider': account.provider,
                'uid': account.uid,
                'extra_data': account.extra_data,
                'date_joined': account.date_joined,
                'last_login': account.last_login
            })

        return Response({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'social_accounts': social_account_list
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        user = request.user
        account_id = request.data.get('account_id')

        if not account_id:
            return Response({'error': '必須提供 account_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = SocialAccount.objects.get(id=account_id, user=user)
        except SocialAccount.DoesNotExist:
            return Response({'error': '找不到指定的社交帳號或該帳號不屬於當前用戶'}, status=status.HTTP_404_NOT_FOUND)

        # 檢查用戶是否只有一個社交帳號
        if SocialAccount.objects.filter(user=user).count() == 1:
            return Response({'error': '無法解除綁定最後一個社交帳號'}, status=status.HTTP_400_BAD_REQUEST)

        account.delete()
        return Response({'message': '社交帳號已成功解綁'}, status=status.HTTP_200_OK)