from django.contrib import admin

from users.models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name'
    )
    list_filter = (
        'email',
        'first_name',
        'last_name'
    )


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author'
    )
    search_fields = (
        'user',
        'author'
    )
