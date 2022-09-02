from django.db import models

# Create your models here.

from django.contrib.auth.models import User

from .utils import path_and_rename


class UserProfile(models.Model):
    """Customized user profile."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    displayname = models.CharField(max_length=50)
    realname = models.CharField(max_length=50, null=True)
    privilege = models.IntegerField(default=0)  # account privilege
    phone = models.CharField(default='""', max_length=20, null=True)
    estdate = models.DateField(auto_now_add=True)
    actdate = models.DateField(null=True)
    expdate = models.DateField(null=True)
    actstat = models.BooleanField(default=True)
    permission_online = models.IntegerField(
        default=0
    )  # 0 is normal account , >0 is online/pay2go account.

    def __str__(self):
        return f"{self.user.username} Profile"
