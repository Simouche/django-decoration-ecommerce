from django.contrib.postgres.fields import ArrayField, DateRangeField
from django.db import models
from django.db.models import Model

from base_backend.models import DeletableModel, do_nothing
from base_backend import _


# Create your models here.

class Category(DeletableModel):
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Name'))
    name_ar = models.CharField(max_length=50, unique=True, verbose_name=_('Arabic Name'))
    name_en = models.CharField(max_length=50, unique=True, verbose_name=_('English Name'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class SubCategory(DeletableModel):
    name = models.CharField(max_length=50, verbose_name=_('Name'))
    name_ar = models.CharField(max_length=50, verbose_name=_('Arabic Name'))
    name_en = models.CharField(max_length=50, verbose_name=_('English Name'))
    category = models.ForeignKey('Category', related_name='sub_categories', verbose_name=_('Category'),
                                 on_delete=do_nothing)

    class Meta:
        unique_together = (('name', 'category'),)
        verbose_name = _('Sub-Category')
        verbose_name_plural = _('Sub-Categories')


class Product(DeletableModel):
    name = models.CharField(max_length=50, verbose_name=_('name'))
    name_ar = models.CharField(max_length=50, verbose_name=_('Arabic Name'))
    name_en = models.CharField(max_length=50, verbose_name=_('English Name'))
    description = models.TextField(verbose_name=_('Description'))
    description_ar = models.TextField(verbose_name=_('Arabic Description'))
    description_en = models.TextField(verbose_name=_('English Description'))
    price = models.DecimalField(verbose_name=_('Price'), max_digits=10, decimal_places=2)
    main_image = models.ImageField(verbose_name=_('Main Image'), upload_to='products')  # ToDo add save to
    slider = ArrayField(models.CharField(max_length=255, ))
    discount_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Discount Price'))
    colors = ArrayField(base_field=models.CharField(max_length=20), verbose_name=_('Available Colors'))
    dimensions = models.CharField(max_length=30, verbose_name=_('Dimensions'))
    stock = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    category = models.ForeignKey('SubCategory', on_delete=do_nothing, related_name='products',
                                 verbose_name=_('Category'), null=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')


class OrderLine(DeletableModel):
    product = models.ForeignKey('Product', related_name='orders_lines', on_delete=do_nothing)
    order = models.ForeignKey('Order', related_name='lines', on_delete=do_nothing)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Quantity'))
    on_discount = models.BooleanField(default=False, verbose_name=_('On Discount'))

    class Meta:
        verbose_name = _('Order Line')
        verbose_name_plural = _('Order Lines')


class Order(DeletableModel):
    status_choices = (('P', _('Pending')), ('CO', _('Confirmed')), ('CA', _('Canceled')))

    profile = models.ForeignKey('accounts.Profile', related_name='orders', on_delete=do_nothing)
    number = models.CharField(max_length=16, unique=True, verbose_name=_('Order Number'))
    status = models.CharField(max_length=2, choices=status_choices, verbose_name=_('Order Status'))

    @property
    def products_count(self):
        return 0

    @property
    def total_sum(self):
        return 0

    @property
    def lines(self):
        return self.lines.filter(visible=True)

    @staticmethod
    def generate_number():
        from random import randint
        return randint(11111, 99999)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')


class Favorite(DeletableModel):
    profile = models.ForeignKey('accounts.Profile', related_name='favorites', on_delete=do_nothing)
    product = models.ForeignKey('Product', related_name='favorites', on_delete=do_nothing)

    class Meta:
        verbose_name = _('Favorite')
        verbose_name_plural = _('Favorites')


class Rate(DeletableModel):
    stars = models.DecimalField(max_digits=1, decimal_places=1, verbose_name=_('Stars'))
    comment = models.CharField(max_length=255, null=True, verbose_name=_('Comment'))
    profile = models.ForeignKey('accounts.Profile', related_name='ratings', on_delete=do_nothing)
    product = models.ForeignKey('Product', related_name='ratings', on_delete=do_nothing)

    class Meta:
        verbose_name = _('Rating')
        verbose_name_plural = _('Ratings')


class Like(DeletableModel):
    profile = models.ForeignKey('accounts.Profile', related_name='likes', on_delete=do_nothing)
    product = models.ForeignKey('Product', related_name='likes', on_delete=do_nothing)

    class Meta:
        verbose_name = _('Like')
        verbose_name_plural = _('Likes')


class CartLine(DeletableModel):
    product = models.ForeignKey('Product', related_name='cart_lines', on_delete=do_nothing)
    cart = models.ForeignKey('Cart', related_name='lines', on_delete=do_nothing)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Quantity'))

    class Meta:
        verbose_name = _('Cart Line')
        verbose_name_plural = _('Cart Lines')


class Cart(DeletableModel):
    profile = models.OneToOneField('accounts.Profile', related_name='carts', on_delete=do_nothing)

    @property
    def products_count(self):
        return 0

    @property
    def total_sum(self):
        return 0

    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')


class SeasonalDiscount(DeletableModel):
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Name'))
    name_ar = models.CharField(max_length=50, unique=True, verbose_name=_('Arabic Name'))
    name_en = models.CharField(max_length=50, unique=True, verbose_name=_('English Name'))
    period = DateRangeField(verbose_name=_('Period'))
    global_discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name=_('Discount'))
    products = models.ManyToManyField('Product', through='ProductOnSeasonalDiscount')

    class Meta:
        verbose_name = _('Seasonal Discount')
        verbose_name_plural = _('Seasonal Discounts')


class ProductOnSeasonalDiscount(DeletableModel):
    product = models.ForeignKey('Product', related_name='seasonal_discounts', on_delete=do_nothing)
    seasonal_discount = models.ForeignKey('SeasonalDiscount', on_delete=do_nothing)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name=_('Discount'))

    class Meta:
        verbose_name = _('Product On Seasonal Discount')
        verbose_name_plural = _('Products On Seasonal Discount')


class DeliveryFee(DeletableModel):
    region = models.ForeignKey('accounts.Region', related_name='fees', on_delete=do_nothing)
    fee = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = _('Delivery Fee')
        verbose_name_plural = _('Delivery Fees')
