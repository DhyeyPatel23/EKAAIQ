# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import Group
# from .models import User

# class UserAdmin(BaseUserAdmin):
#     # The fields to be used in displaying the User model.
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_student', 'is_teacher', 'is_staff')
#     list_filter = ('is_student', 'is_teacher', 'is_staff', 'is_superuser', 'is_active', 'groups')

#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}),
#         ('Role', {'fields': ('is_student', 'is_teacher')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'password1', 'password2', 'is_student', 'is_teacher', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
#         }),
#     )
#     search_fields = ('username', 'first_name', 'last_name', 'email')
#     ordering = ('username',)
#     filter_horizontal = ('groups', 'user_permissions',)

# # Register the custom User model with the custom UserAdmin
# admin.site.register(User, UserAdmin)

# # Unregister the Group model from admin if you don't want it accessible in the admin panel
# admin.site.unregister(Group)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User

class UserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    list_display = ('email', 'first_name', 'last_name', 'is_student', 'is_teacher', 'is_staff')
    list_filter = ('is_student', 'is_teacher', 'is_staff', 'is_superuser', 'is_active', 'groups')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # Replace 'username' with 'email'
        ('Personal info', {'fields': ('first_name', 'last_name')}),  # No need for 'email' here, it's already in the main fieldset
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}), 
        ('Role', {'fields': ('is_student', 'is_teacher')}), 
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_student', 'is_teacher', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')  # Replace 'username' with 'email'
    ordering = ('email',)  # Order by 'email'
    filter_horizontal = ('groups', 'user_permissions',)

# Register the custom User model with the custom UserAdmin
admin.site.register(User, UserAdmin)

# Unregister the Group model from admin if you don't want it accessible in the admin panel
admin.site.unregister(Group)
