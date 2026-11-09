from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class ClinicUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'first_name',
            'last_name',
            'mobile_number',
            'staff_role',
            'specialization',
            'license_number',
        )


class ClinicUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = ClinicUserCreationForm
    form = ClinicUserChangeForm
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'staff_role', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'staff_role')
    search_fields = ('email', 'first_name', 'last_name', 'mobile_number')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'mobile_number', 'specialization', 'license_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'staff_role')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'first_name',
                'last_name',
                'mobile_number',
                'staff_role',
                'specialization',
                'license_number',
                'password1',
                'password2',
                'is_staff',
                'is_superuser',
                'is_active',
            ),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
