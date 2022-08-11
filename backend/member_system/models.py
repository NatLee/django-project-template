from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

from django.utils.translation import gettext_lazy as _


class MemberAccountManager(BaseUserManager):
    """Manager for user profiles"""

    def new_user(self, email, username, password=None):
        """Create a new user profile"""
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("User must have a name")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, username, password, permission=None):
        """Create a new user profile"""
        user = self.new_user(email, username, password)
        user.save(using=self._db)

    def create_superuser(self, email, username, password):
        """Create a new superuser profile"""
        user = self.new_user(email, username, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user

    def update_user(self, id_, email, username, password=None):
        """Update user profile"""
        email = self.normalize_email(email)
        user = MemberAccount.objects.get(id=id_)
        if password != None and password.strip() != "":
            user.password = password
            user.set_password(user.password)
        user.email = email
        user.username = username
        user.save()

    def delete_user(self, user):
        # user = MemberAccount.objects.get(id=id_)
        if user.is_superuser != True:
            user.delete()

    def update_member_control_member(
        self, user, email, username, password, user_permission, is_active, is_staff
    ):
        """Update member control profile"""
        email = self.normalize_email(email)
        # user = MemberAccount.objects.get(id=id_)
        if user.is_superuser != True:
            if password != None and password.strip() != "":
                user.password = password
                user.set_password(user.password)
            user.email = email
            user.username = username
            user.user_permission_id = user_permission
            user.is_active = is_active
            user.is_staff = is_staff
            user.save()


class MemberAccount(AbstractBaseUser, PermissionsMixin):
    """Database model for users in the system"""

    email = models.EmailField(max_length=255, unique=True, verbose_name="Email")
    username = models.CharField(max_length=255, unique=True, verbose_name="帳號名稱")
    is_staff = models.BooleanField(default=False, verbose_name="管理員")
    is_active = models.BooleanField(default=True, verbose_name="啟用帳號")
    is_superuser = models.BooleanField(default=False, verbose_name="超級使用者")
    is_delete = models.BooleanField(default=False, verbose_name="軟刪除")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立日期")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日期")
    objects = MemberAccountManager()
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        """Return string representation of our user"""
        return self.username
