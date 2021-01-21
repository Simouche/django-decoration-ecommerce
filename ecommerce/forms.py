from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.forms import inlineformset_factory

from accounts.models import User
from ecommerce.models import Order, OrderLine, Product, SubCategory, Category
from base_backend import _
from ecommerce.widgets import BootstrapTimePickerInput, BootstrapDatePickerInput


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


class CreateProductForm(BSModalModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': _('French Name'),
        }
    ), label=_('French Name'))

    name_ar = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': _('Arabic Name')
        }
    ), label=_('Arabic Name'))

    name_en = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': _('English Name')
        }
    ), label=_('English Name'))

    description = forms.CharField(widget=forms.Textarea(
        attrs={
            'placeholder': _('French Description'),
            'size': 20
        }
    ), label=_('French Description'))

    description_ar = forms.CharField(widget=forms.Textarea(
        attrs={
            'placeholder': _('Arabic Description')
        }
    ), label=_('Arabic Description'))

    description_en = forms.CharField(widget=forms.Textarea(
        attrs={
            'placeholder': _('English Description')
        }
    ), label=_('English Description'))

    price = forms.DecimalField(widget=forms.NumberInput(
        attrs={
            'placeholder': _('Price')
        }
    ), label=_('Price'))
    main_image = forms.ImageField(widget=forms.FileInput(
        attrs={
            'placeholder': _('Main Image')
        }
    ), label=_('Main Image'))

    discount_price = forms.DecimalField(widget=forms.NumberInput(
        attrs={
            'placeholder': _('Discount Price')
        }
    ), label=_('Discount Price'))

    colors = SimpleArrayField(base_field=forms.CharField(), widget=forms.TextInput(
        attrs={
            'placeholder': _('Available Colors')
        }
    ), label=_('Available Colors'))

    dimensions = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': _('Dimensions')
        }
    ), label=_('Dimensions'))

    stock = forms.DecimalField(widget=forms.NumberInput(
        attrs={
            'placeholder': _('Stock')
        }
    ), label=_('Stock'))

    category = forms.ModelChoiceField(queryset=SubCategory.objects.filter(visible=True))

    class Meta:
        model = Product
        fields = ['name', 'name_ar', 'name_en', 'description', 'description_ar', 'description_en', 'price',
                  'main_image', 'discount_price', 'colors', 'dimensions', 'stock', 'category']


class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'name_ar', 'name_en']


class CreateSubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['name', 'name_en', 'name_ar', 'category']


CategoryWithSubCatsFormSet = inlineformset_factory(parent_model=Category, model=SubCategory,
                                                   fields=['name', 'name_en', 'name_ar'], can_delete=True, extra=1)


class SearchOrderStatusChangeHistory(forms.Form):
    FROM_STATUS_CHOICES = (('O', _('Old Status')),) + Order.status_choices
    TO_STATUS_CHOICES = (('N', _('New Status')),) + Order.status_choices

    date = forms.DateField(required=False, input_formats=['%d/%m/%Y'], widget=BootstrapDatePickerInput())
    time = forms.TimeField(required=False, input_formats=['%H:%M'], widget=BootstrapTimePickerInput())
    user = forms.ModelChoiceField(queryset=User.objects.exclude(user_type='C'), required=False, empty_label=_('User'))
    order = forms.ModelChoiceField(queryset=Order.objects.all(), required=False, empty_label=_('Order'))
    from_status = forms.ChoiceField(choices=FROM_STATUS_CHOICES, required=False)
    to_status = forms.ChoiceField(choices=TO_STATUS_CHOICES, required=False)

    def clean_from_status(self):
        if self.cleaned_data.get('from_status') == 'O':
            return None
        return self.cleaned_data.get('from_status')

    def clean_to_status(self):
        if self.cleaned_data.get('to_status') == 'N':
            return None
        return self.cleaned_data.get('to_status')
