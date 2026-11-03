from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from userprofile.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    """Import/export buttons (django-import-export) and a change history (django-simple-history)."""

    list_display = ("user", "displayname", "description")
    list_select_related = ("user",)
    search_fields = ("user__username", "displayname")
