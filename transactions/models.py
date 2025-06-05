from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural ='Categories'

    def __str__(self):
        return self.name

class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20)
    current_balance = models.IntegerField(default=0)


    def __str__(self):
        return f'{self.user.username} - {self.account_number}'

class Transaction(models.Model):
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)  # Unique identifier
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=[('credit', 'Credit'), ('debit', 'Debit')])
    timestamp = models.DateTimeField()  # Timestamp of the transaction
    description = models.TextField(blank=True)  # Parsed description from the SMS
    category = models.CharField(max_length=266,default="")
    new_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    payment_type = models.CharField(max_length=255, default='Cash')
    is_debited = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.transaction_type} - Rs.{self.amount} on {self.timestamp}'