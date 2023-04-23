from django.contrib import admin
from transactions.models import Balance, BalanceTransfer, PaymentRequest


class BalanceTransferAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender_email', 'recipient_email', 'currency', 'amount', 'date')
    list_filter = ('currency',)
    search_fields = ('id', 'sender_email', 'recipient_email')
    list_per_page = 10


admin.site.register(BalanceTransfer, BalanceTransferAdmin)


class BalanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'currency', 'amount')
    search_fields = ('id', 'user', 'currency')
    list_per_page = 10

    @admin.display(ordering='user__id', description='UserID')
    def get_userid(self, obj):
        return obj.user.id


admin.site.register(Balance, BalanceAdmin)


class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'sender_email', 'recipient_email', 'currency', 'amount', 'start_date', 'status', 'closed_date')
    list_filter = ('currency', 'status')
    search_fields = ('id', 'sender_email', 'recipient_email', 'currency', 'amount', 'start_date')
    list_per_page = 10


admin.site.register(PaymentRequest, PaymentRequestAdmin)
