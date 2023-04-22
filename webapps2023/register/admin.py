from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Balance
from .forms import CustomUserCreationForm, CustomUserCreationFormAdmin, CustomUserChangeForm
from register.management.user_groups import UserGroups


# Register your models here.
class CustomUserAdmin(UserAdmin):
    # The forms to add and change users
    add_form = CustomUserCreationFormAdmin
    form = CustomUserChangeForm

    model = CustomUser

    # Fields to be used in displaying the CustomUser model
    # Override the definitions on the UserAdmin
    list_display = ('id', 'email', 'username', 'first_name', 'last_name', 'currency', 'balance', 'is_admin', 'change_password', 'created_at')
    list_filter = ('currency', 'is_admin')
    fieldsets = (
        (None, {"fields": ("email", "username", "first_name", "last_name", "currency", "password", "is_active", 'change_password')}),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
    )
    admin_readonly_fields = ("currency", "groups", "user_permissions")
    add_fieldsets = (
        (None, {
            "classes": ["wide"],
            "fields": [
                "email", "username", "first_name", "last_name", "is_admin"
            ]}
         ),
    )
    search_fields = ('id', 'email', 'username', 'first_name', 'last_name', 'currency')
    ordering = ('id',)
    list_per_page = 10

    # OVERRIDE USERADMIN DEFAULT METHODS

    def get_list_display(self, request):
        # Add superuser column only for superusers
        # Regular admins shouldn't be able to see that
        if request.user.is_superuser:
            return self.list_display.__add__(('is_superuser',))
        else:
            return super(CustomUserAdmin, self).get_list_display(request)

    def get_readonly_fields(self, request, obj=None):
        # Restrict some fields to be read-only for admins
        # Can probably remove this in the final version
        # Admins shouldn't have permission to modify anything
        if request.user.groups.filter(name=UserGroups.ADMINS.value):
            return self.admin_readonly_fields
        else:
            return super(CustomUserAdmin, self).get_readonly_fields(request,obj=obj)

    def response_add(self, request, obj, post_url_continue=None):
        # Generate a random password for the administrator
        # Show it on screen
        # The admin will have to reset it on first login
        rand_password = CustomUser.objects.make_random_password()
        obj.set_password(rand_password)
        obj.save()
        self.message_user(request, f'The password for {obj.username} is {rand_password}.')
        return super().response_add(request, obj, post_url_continue)


admin.site.register(CustomUser, CustomUserAdmin)


class BalanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_userid', 'currency', 'amount')
    search_fields = ('id', 'get_userid', 'currency')
    list_per_page = 10

    @admin.display(ordering='user__id', description='UserID')
    def get_userid(self, obj):
        return obj.user.id


admin.site.register(Balance, BalanceAdmin)
