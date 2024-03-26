from django import forms

class PaymentForm(forms.Form):
    amount = forms.DecimalField(required=True, label="Amount")
    description = forms.CharField(required=False, label="Description")

    class Meta:
        fields = ['amount', 'description']


