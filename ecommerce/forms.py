from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.forms import inlineformset_factory

from accounts.models import User, City
from base_backend import _
from ecommerce.models import Order, OrderLine, Product, SubCategory, Category, IndexContent, DeliveryCompany, \
    DeliveryFee, DeliveryGuy, CartLine, Cart
from ecommerce.widgets import BootstrapTimePickerInput, BootstrapDatePickerInput

status_choices = (('P', _('Pending')),
                  ('RC', _('RECALL')),
                  ('CO', _('Confirmed')),
                  ('CA', _('Canceled')),)


class CreateOrderForm(forms.ModelForm):
    number = forms.IntegerField(widget=forms.NumberInput(
        attrs={
            'placeholder': _('Number'),
            'readonly': True
        }
    ))
    assigned_to = forms.ModelChoiceField(queryset=User.objects.filter(user_type='CA'), required=False)

    def __init__(self, is_caller=False, *args, **kwargs):
        super(CreateOrderForm, self).__init__(*args, **kwargs)
        if is_caller:
            self.status_choices = (('P', _('Pending')),
                                   ('RC', _('RECALL')),
                                   ('CO', _('Confirmed')),
                                   ('CA', _('Canceled')),)
            self.fields['status'] = forms.ChoiceField(choices=self.status_choices)

    class Meta:
        global status_choices
        model = Order
        fields = ['profile', 'number', 'status', 'shipping_fee', 'free_delivery', 'note', 'delivery_date']


class CreateOrderLineForm(forms.ModelForm):
    order = forms.ModelChoiceField(queryset=Order.objects.filter(visible=True), required=False)

    class Meta:
        model = OrderLine
        fields = ['product', 'order', 'quantity']


OrderWithLinesFormSet = inlineformset_factory(parent_model=Order, model=OrderLine, form=CreateOrderLineForm,
                                              can_delete=True)


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
    ), label=_('Arabic Name'), required=False)

    name_en = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': _('English Name')
        }
    ), label=_('English Name'), required=False)

    description = forms.CharField(widget=forms.Textarea(
        attrs={
            'placeholder': _('French Description'),
            'size': 20
        }
    ), label=_('French Description'), required=False)

    description_ar = forms.CharField(widget=forms.Textarea(
        attrs={
            'placeholder': _('Arabic Description')
        }
    ), label=_('Arabic Description'), required=False)

    description_en = forms.CharField(widget=forms.Textarea(
        attrs={
            'placeholder': _('English Description')
        }
    ), label=_('English Description'), required=False)

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
    ), label=_('Discount Price'), required=False)

    colors = SimpleArrayField(base_field=forms.CharField(), widget=forms.TextInput(
        attrs={
            'placeholder': _('Available Colors')
        }
    ), label=_('Available Colors'), required=False)

    dimensions = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': _('Dimensions')
        }
    ), label=_('Dimensions'), required=False)

    stock = forms.DecimalField(widget=forms.NumberInput(
        attrs={
            'placeholder': _('Stock')
        }
    ), label=_('Stock'), required=False)

    category = forms.ModelChoiceField(queryset=SubCategory.objects.filter(visible=True))

    class Meta:
        model = Product
        fields = ['name', 'name_ar', 'name_en', 'description', 'description_ar', 'description_en', 'price',
                  'main_image', 'discount_price', 'colors', 'dimensions', 'stock', 'category', 'free_delivery',
                  'reference']


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


class IndexContentForm(forms.ModelForm):
    class Meta:
        model = IndexContent
        fields = ['card1_visibility', 'card1_header', 'card1_title', 'card1_content', 'card1_button_text',
                  'card1_image', 'section1_title', 'section1_text', 'section1_categories', 'section2_title',
                  'section2_text', 'section2_button_text', 'section2_image', 'section3_title', 'section3_text',
                  'section3_button_text', 'section4_title', 'section4_text', 'section4_button_text', 'section4_image1',
                  'section4_image2', 'section5_title', 'section5_text', 'section5_button_text', 'facebook', 'Instagram',
                  'twitter']


class CreateDeliveryCompanyForm(forms.ModelForm):
    class Meta:
        model = DeliveryCompany
        fields = ('company_name', 'weight_threshold')


class CreateDeliveryFeeForm(forms.ModelForm):
    class Meta:
        model = DeliveryFee
        fields = ('company', 'state', 'fee')


CompanyFeesFormset = inlineformset_factory(DeliveryCompany, DeliveryFee, form=CreateDeliveryFeeForm, extra=48)


class CreateDeliveryGuyForm(forms.ModelForm):
    class Meta:
        model = DeliveryGuy
        fields = ('name', 'company')


class CartLineForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.filter(visible=True))
    price = forms.DecimalField(required=False)
    quantity = forms.DecimalField()
    total = forms.DecimalField(required=False)

    def __init__(self, *args, editable=False, **kwargs):
        initial = kwargs.get('initial', {})
        initial['price'] = kwargs.get('instance').product.price
        initial['total'] = kwargs.get('instance').total
        kwargs['initial'] = initial
        super(CartLineForm, self).__init__(*args, **kwargs)
        if not editable:
            self.fields['product'].widget.attrs['disabled'] = 'disabled'
            self.fields['price'].widget.attrs['readonly'] = True
            self.fields['total'].widget.attrs['readonly'] = True

    class Meta:
        model = CartLine
        fields = ('product', 'cart', 'quantity')


CartWithLinesFormSet = inlineformset_factory(parent_model=Cart, model=CartLine, form=CartLineForm, extra=0)


class AssignOrdersToCallerForm(forms.Form):
    orders = forms.ModelMultipleChoiceField(queryset=Order.objects.filter(visible=True))
    caller = forms.ModelChoiceField(queryset=User.objects.filter(user_type='CA'))


class CheckoutForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    phone_number = forms.CharField(required=False)
    email_address = forms.EmailField(required=False)
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False)
    address = forms.CharField(widget=forms.Textarea(), required=False)
    note = forms.CharField(widget=forms.Textarea(attrs={"placeholder": _("Note")}), required=False)

    def save(self, user: User):
        cd = self.cleaned_data
        user.first_name = cd.get('first_name', user.first_name)
        user.last_name = cd.get('last_name', user.last_name)
        user.phones.append(cd.get('phone_number'))
        user.profile.city = cd.get('city', user.profile.city)
        user.profile.address = cd.get('address', user.profile.address)
        user.profile.save()
        user.save()


class OrderFilter(forms.Form):
    FROM_STATUS_CHOICES = Order.status_choices

    order = forms.ModelChoiceField(queryset=Order.objects.all(), required=False, empty_label=_('Numero'))
    user = forms.ModelChoiceField(queryset=User.objects.filter(user_type='C'), required=False, empty_label=_('Client'))
    delivery_man = forms.ModelChoiceField(queryset=DeliveryGuy.objects.all(), required=False,
                                          empty_label=_('Delivery Man'))
    caller = forms.ModelChoiceField(queryset=User.objects.exclude(user_type='C'), required=False,
                                    empty_label=_('Caller'))
    start_date = forms.DateField(required=False, input_formats=['%d/%m/%Y'], widget=BootstrapDatePickerInput())
    end_date = forms.DateField(required=False, input_formats=['%d/%m/%Y'], widget=BootstrapDatePickerInput())
    status = forms.MultipleChoiceField(choices=FROM_STATUS_CHOICES, required=False)
