from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth.models import User

from .models import UserProfile, Settings


@admin.action(description="Активировать неактивных пользователей")
def activate_users(modeladmin, request, queryset):
    for user in queryset:
        user.profile.restore()
        user.is_active = True
        user.save()


class CustomChangeList(ChangeList):
    def get_queryset(self, request):
        if "inactive" in request.GET:
            return User.objects.filter(is_active=False)
        else:
            return super().get_queryset(request)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_staff", "is_active",)
    list_display_links = ("username", "email",)
    list_editable = ("is_staff", "is_active",)
    list_select_related = ("profile",)
    fieldsets = [
        ("Базовая информация", {"fields": ["username", "first_name", "last_name", "email", "is_staff", "is_active", ]})]
    inlines = [UserProfileInline]
    actions = [activate_users]

    def delete_queryset(self, request, queryset):
        for user in queryset:
            user.profile.delete()
            user.is_active = False
            user.save()

    def get_changelist(self, request, **kwargs):
        return CustomChangeList


class SettingsAdmin(admin.ModelAdmin):
    list_display = ("pk", "general_phone", "general_email", "general_address",)
    list_display_links = ("pk",)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Settings, SettingsAdmin)
