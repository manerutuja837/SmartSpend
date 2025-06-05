from django.db import models
from django.contrib.auth.models import User

class PaycheckPeriod(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    def __str__(self):
        return f"Paycheck Period: {self.id} - {self.start_date} to {self.end_date} "

class Income(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    paycheck_period = models.ForeignKey(PaycheckPeriod, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=255)
    def __str__(self):
        return f"Income: {self.id} - {self.source} - {self.amount} for {self.user.username}"

class Savings(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    paycheck_period = models.ForeignKey(PaycheckPeriod, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Savings: {self.id} - {self.purpose} - {self.amount} for {self.user.username}"

class Bill(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    paycheck_period = models.ForeignKey(PaycheckPeriod, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"Bill: {self.id} - {self.description} - {self.amount} for {self.user.username}"


class DailyExpense(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    paycheck_period = models.ForeignKey(PaycheckPeriod, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"Daily Expense: {self.id} - {self.description} - {self.amount} for {self.user.username}"

class Loan(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    paycheck_period = models.ForeignKey(PaycheckPeriod, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"Loan: {self.id} - {self.description} - {self.amount} for {self.user.username}"