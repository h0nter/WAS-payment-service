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
    list_display = ('id', 'email', 'username', 'first_name', 'last_name', 'currency', 'balance')
    list_filter = ('id', 'email', 'username', 'first_name', 'last_name', 'currency')
    fieldsets = (
        (None, {"fields": ("email", "username", "first_name", "last_name", "currency", "password", "is_active")}),
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

    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name=UserGroups.ADMINS.value):
            return self.admin_readonly_fields
        else:
            return super(CustomUserAdmin, self).get_readonly_fields(request,obj=obj)


admin.site.register(CustomUser, CustomUserAdmin)


class BalanceAdmin(admin.ModelAdmin):
    list_display = ('id','get_userid','currency','amount')
    search_fields = ('id','get_userid','currency')
    list_per_page = 10

    @admin.display(ordering='user__id', description='UserID')
    def get_userid(self, obj):
        return obj.user.id


admin.site.register(Balance, BalanceAdmin)
