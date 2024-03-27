from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser, Subscriptions


@register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("pk", "username", "email", "first_name", "last_name")
    list_filter = ("username", "email")
    search_fields = ("username", "email")


@register(Subscriptions)
class SubscriptionsAdmin(ModelAdmin):
    list_display = ("pk", "user", "author")
    search_fields = ("user", "author")
    list_filter = ("user", "author")
