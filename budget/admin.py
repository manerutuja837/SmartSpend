from django.contrib import admin

# Register your models here.
from .models import PaycheckPeriod, Income, Savings, Bill, DailyExpense, Loan

admin.site.register(PaycheckPeriod)
admin.site.register(Income)
admin.site.register(Savings)
admin.site.register(Bill)
admin.site.register(DailyExpense)
admin.site.register(Loan)