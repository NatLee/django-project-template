from django.contrib import admin
from django_login_history.models import Login
from django.urls import path
from django.http import JsonResponse

from unfold.admin import ModelAdmin

@admin.register(Login)
class LoginModelAdmin(ModelAdmin):
    actions = None
    model = Login
    change_list_template = 'admin/login/change_list.html'
    list_per_page = 10

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.method in ["GET", "HEAD"] and super().has_change_permission(
            request, obj
        )

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ('pk', 'user', 'get_displayname', 'ip', 'date', 'country', 'region', 'city')
    list_filter = ('user', 'date', 'country', 'region', 'city')
    search_fields = ('user__username', 'ip', 'country', 'region', 'city')


    def get_displayname(self, obj):
        return obj.user.userprofile.displayname
    get_displayname.short_description = '使用者名稱'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('chart-data/', self.admin_site.admin_view(self.chart_data_view), name='login_chart_data'),
        ]
        return custom_urls + urls

    def chart_data_view(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        data = Login.get_all_users_login_count_by_date_range(start_date, end_date)
        return JsonResponse(data, safe=False)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_chart'] = True
        return super().changelist_view(request, extra_context=extra_context)