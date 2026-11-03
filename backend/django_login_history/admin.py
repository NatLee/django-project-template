from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from django_login_history.models import Login


@admin.register(Login)
class LoginModelAdmin(admin.ModelAdmin):
    """Read-only list of logins with a chart of logins per user per day."""

    actions = None
    change_list_template = "admin/login/change_list.html"
    list_per_page = 10
    list_display = ("pk", "user", "get_displayname", "ip", "date", "country", "region", "city")
    list_filter = ("user", "date", "country", "region", "city")
    list_select_related = ("user__userprofile",)
    search_fields = ("user__username", "ip", "country", "region", "city")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.method in ["GET", "HEAD"] and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="使用者名稱")
    def get_displayname(self, obj):
        profile = getattr(obj.user, "userprofile", None)
        return getattr(profile, "displayname", "")

    def get_urls(self):
        custom_urls = [
            path("chart-data/", self.admin_site.admin_view(self.chart_data_view), name="login_chart_data"),
        ]
        return custom_urls + super().get_urls()

    def chart_data_view(self, request):
        try:
            data = Login.get_all_users_login_count_by_date_range(
                request.GET.get("start_date", ""), request.GET.get("end_date", "")
            )
        except ValueError:
            return JsonResponse({"error": "start_date and end_date must be YYYY-MM-DD"}, status=400)
        return JsonResponse(data, safe=False)

    def changelist_view(self, request, extra_context=None):
        extra_context = {**(extra_context or {}), "show_chart": True}
        return super().changelist_view(request, extra_context=extra_context)
