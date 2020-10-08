from django import forms
from django.forms import inlineformset_factory

from ecommerce.models import Order, OrderLine


class CreateOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['profile', 'number', 'status']


class CreateOrderLineForm(forms.ModelForm):
    order = forms.ModelChoiceField(queryset=Order.objects.filter(visible=True), required=False)

    class Meta:
        model = OrderLine
        fields = ['product', 'order', 'quantity', 'quantity']


OrderWithLinesFormSet = inlineformset_factory(parent_model=Order, model=OrderLine, fields=['product', 'quantity'],
                                              can_delete=True, extra=1)
