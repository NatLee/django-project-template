import logging
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.dispatch import receiver
from django.utils import timezone
from django_q.tasks import async_task

from django_login_history.utils.get_client_ip import get_client_ip

logger = logging.getLogger(__name__)


class Login(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="使用者")
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
            models.Index(fields=["user", "date"]),
            models.Index(fields=["ip"]),
        ]
        verbose_name = "登入記錄（Login History）"
        verbose_name_plural = "登入記錄（Login History）"

    @classmethod
    def cleanup_old_records(cls) -> int:
        """Delete records older than LOGIN_HISTORY_RETENTION_DAYS; returns how many were deleted."""
        cutoff = timezone.now() - timedelta(days=settings.LOGIN_HISTORY_RETENTION_DAYS)
        deleted, _ = cls.objects.filter(date__lt=cutoff).delete()
        return deleted

    @classmethod
    def get_all_users_login_count_by_date_range(cls, start_date: str, end_date: str) -> list[dict]:
        """One row per user per day between two YYYY-MM-DD dates (inclusive), with that day's login count.

        Raises ValueError when a date is not in YYYY-MM-DD form.
        """
        start_date, end_date = date.fromisoformat(start_date), date.fromisoformat(end_date)
        counts = {
            (row["user__pk"], row["day"]): row["count"]
            for row in cls.objects.filter(date__date__gte=start_date, date__date__lte=end_date)
            .annotate(day=TruncDate("date", tzinfo=timezone.get_current_timezone()))
            .values("user__pk", "day")
            .annotate(count=Count("id"))
        }
        days = [start_date + timedelta(n) for n in range((end_date - start_date).days + 1)]

        result = []
        for user in get_user_model().objects.select_related("userprofile").order_by("username"):
            profile = getattr(user, "userprofile", None)
            displayname = getattr(profile, "displayname", "")
            label = f"[{user.username}]{displayname}" if displayname else user.username
            for day in days:
                result.append(
                    {"id": user.pk, "username": label, "date": day.isoformat(), "count": counts.get((user.pk, day), 0)}
                )
        return result


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    """Record every login. The location lookup runs in the background so login stays fast."""
    login = Login.objects.create(
        user=user,
        ip=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    logger.info("Login recorded: %s", login)
    if login.ip and settings.LOGIN_HISTORY_GEOIP_URL:
        async_task("django_login_history.tasks.fill_location", login.pk)
