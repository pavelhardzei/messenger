from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import UserProfile


class ProfileAdmin(BaseUserAdmin):
    list_display = ('email', 'user_name', 'full_name', 'date_of_birth', 'date_joined', 'is_staff', 'is_superuser')
    list_filter = ('is_superuser', )

    fieldsets = (
        (None, {'fields': ('email', 'is_staff', 'is_superuser', 'password')}),
        ('Personal info', {'fields': ('user_name', 'full_name', 'date_of_birth', 'date_joined')})
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'is_staff', 'is_superuser', 'password1', 'password2')}),
        ('Personal info', {'fields': ('user_name', 'full_name', 'date_of_birth')})
    )

    search_fields = ('email', 'user_name')
    ordering = ('email', )
    filter_horizontal = ()


admin.site.register(UserProfile, ProfileAdmin)
