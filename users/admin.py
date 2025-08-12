from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email','nid','role', 'first_name', 'last_name', 'is_active')
    list_filter = ("role", "is_staff", "is_superuser", "is_active")

    fieldsets = (
        (None, {'fields': ('email','nid', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'contact_number', 'profile_image')}),
        ('Permissions', {'fields': ('role','is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),

    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','nid', 'password1', 'password2','role', 'is_staff', 'is_active')
        }),
    )

    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)