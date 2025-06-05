from django import forms

class WithdrawalForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label="Withdrawal Amount")
