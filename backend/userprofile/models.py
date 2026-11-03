from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords


class UserProfile(models.Model):
    """Extra fields for every user; created automatically when a user is created (see signals.py)."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    displayname = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True, default="")
    history = HistoricalRecords()  # every change shows up under "History" in the admin

    def __str__(self):
        return f"{self.user.username} Profile"

    class Meta:
        verbose_name = "使用者資料（User Profile）"
        verbose_name_plural = "使用者資料（User Profiles）"
