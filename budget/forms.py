# forms.py
from django import forms
from .models import Income, Savings, Bill, DailyExpense, Loan, PaycheckPeriod

class PaycheckPeriodForm(forms.ModelForm):
    class Meta:
        model = PaycheckPeriod
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ('source','amount')

class SavingsForm(forms.ModelForm):
    class Meta:
        model = Savings
        fields = ('purpose','amount')

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ('description','amount')

class DailyExpenseForm(forms.ModelForm):
    class Meta:
        model = DailyExpense
        fields = ('description','amount')

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ('description','amount')


class MonthSelectionForm(forms.Form):
    month = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'month', 'class': 'month-select'}),
    )