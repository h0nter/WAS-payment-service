from django.contrib import admin
from transactions.models import Balance, BalanceTransfer


class BalanceTransferAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender_email', 'recipient_email', 'currency', 'amount')
    search_fields = ('id', 'sender_email', 'recipient_email')
    list_per_page = 10


admin.site.register(BalanceTransfer, BalanceTransferAdmin)


class BalanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_userid', 'currency', 'amount')
    search_fields = ('id', 'get_userid', 'currency')
    list_per_page = 10

    @admin.display(ordering='user__id', description='UserID')
    def get_userid(self, obj):
        return obj.user.id


admin.site.register(Balance, BalanceAdmin)
