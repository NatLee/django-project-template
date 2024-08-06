from typing import Dict, Any, Optional
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from django.db import models
from django.db import transaction
from django.db.models import Count

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

import requests
from requests.exceptions import RequestException

from django_login_history.utils.get_client_ip import get_client_ip

import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class Login(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="使用者")
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP位址")
    user_agent = models.TextField(verbose_name="使用者代理")
    date = models.DateTimeField(auto_now_add=True, verbose_name="登入時間")
    country = models.CharField(max_length=50, blank=True, verbose_name="國家")
    region = models.CharField(max_length=50, blank=True, verbose_name="地區")
    city = models.CharField(max_length=50, blank=True, verbose_name="城市")

    def __str__(self):
        return f"{self.user.username} ({self.ip or '未知IP'}) 於 {self.date}"

    class Meta:
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['ip']),
        ]
        verbose_name = "登入記錄（Login History）"
        verbose_name_plural = "登入記錄（Login History）"

    @classmethod
    def cleanup_old_records(cls):
        # 刪除90天前的記錄
        days_ago = timezone.now() - timedelta(days=90)
        cls.objects.filter(date__lt=days_ago).delete()

    @classmethod
    def get_all_users_login_count_by_date_range(cls, start_date, end_date):
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

        # 獲取所有用戶
        all_users = User.objects.all()

        # 獲取指定日期範圍的登錄資料
        queryset = cls.objects.filter(date__date__gte=start_date, date__date__lte=end_date) \
            .values('user__pk', 'user__username') \
            .annotate(date=models.functions.TruncDate('date', tzinfo=timezone.get_current_timezone())) \
            .annotate(count=Count('id')) \
            .order_by('user__username', 'date')

        # 將查詢結果轉換為字典，方便後續處理
        login_data = {
            (item['user__pk'], item['date'].strftime('%Y-%m-%d')): item['count']
            for item in queryset
        }

        result = []
        for user in all_users:
            user_data = []
            for day in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
                date_str = day.strftime('%Y-%m-%d')
                count = login_data.get((user.pk, date_str), 0)
                username = user.username
                userprofile = getattr(user, 'userprofile', None)
                displayname = None
                if userprofile:
                    displayname = getattr(userprofile, 'displayname', None)
                if displayname:
                    username = f'[{user.username}]{user.userprofile.displayname}'
                user_data.append({
                    'id': user.pk,
                    'username': username,
                    'date': date_str,
                    'count': count
                })
            result.extend(user_data)

        return result



def get_location_data_from_ip(ip: Optional[str]) -> Dict[str, Any]:
    if ip is None:
        return {}

    url = f"http://ip-api.com/json/{ip}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'success':
            return {
                'country': data.get('country', ''),
                'region': data.get('regionName', ''),
                'city': data.get('city', '')
            }
        else:
            logger.warning(f"IP API returned non-success status for IP: {ip}")
            return {}
    except RequestException as e:
        logger.error(f"Error getting location data for IP {ip}: {e}")
        return {}

@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    ip = get_client_ip(request)
    location_info = get_location_data_from_ip(ip)

    try:
        with transaction.atomic():
            login = Login.objects.create(
                user=user,
                ip=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                country=location_info.get('country', ''),
                region=location_info.get('region', ''),
                city=location_info.get('city', ''),
            )
        logger.info(f"Login recorded: {login}")
    except ValidationError as e:
        logger.error(f"Error creating login record: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error creating login record: {e}")