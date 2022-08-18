from django.forms import ModelForm
from orders.models import Payment


class PaymentForm(ModelForm):
    mdoel = Payment
    exclide = ['user', ]