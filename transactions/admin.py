from django.contrib import admin
from .models import BankAccount, Category, Transaction
# Register your models here.

class TransactionAdmin(admin.ModelAdmin):
    list_display=('account','timestamp','amount','category')
    search_fields=('date','amount','category')

admin.site.register(Transaction,TransactionAdmin)
# admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(BankAccount)