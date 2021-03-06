import decimal

from django.contrib.postgres.fields import ArrayField, DateRangeField
from django.db import models
from django.db.models import Model, Sum, Avg, F

from base_backend.models import DeletableModel, do_nothing, BaseModel, cascade
from base_backend import _

# Create your models here.
from ecommerce.managers import CustomCategoryManager


class Category(DeletableModel):
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Name'))
    name_ar = models.CharField(max_length=50, unique=True, verbose_name=_('Arabic Name'), null=True, blank=True)
    name_en = models.CharField(max_length=50, unique=True, verbose_name=_('English Name'), null=True, blank=True)

    objects = CustomCategoryManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class SubCategory(DeletableModel):
    name = models.CharField(max_length=50, verbose_name=_('Name'))
    name_ar = models.CharField(max_length=50, verbose_name=_('Arabic Name'), null=True, blank=True)
    name_en = models.CharField(max_length=50, verbose_name=_('English Name'), null=True, blank=True)
    category = models.ForeignKey('Category', related_name='sub_categories', verbose_name=_('Category'),
                                 on_delete=do_nothing)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'category'),)
        verbose_name = _('Sub-Category')
        verbose_name_plural = _('Sub-Categories')


class Product(DeletableModel):
    name = models.CharField(max_length=50, verbose_name=_('name'))
    name_ar = models.CharField(max_length=50, verbose_name=_('Arabic Name'), null=True, blank=True)
    name_en = models.CharField(max_length=50, verbose_name=_('English Name'), null=True, blank=True)
    description = models.TextField(verbose_name=_('Description'))
    description_ar = models.TextField(verbose_name=_('Arabic Description'), null=True, blank=True)
    description_en = models.TextField(verbose_name=_('English Description'), null=True, blank=True)
    price = models.DecimalField(verbose_name=_('Price'), max_digits=10, decimal_places=2)
    main_image = models.ImageField(verbose_name=_('Main Image'), upload_to='products')
    slider = ArrayField(models.CharField(max_length=255, ), null=True, blank=True, default=list)
    discount_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Discount Price'), null=True,
                                         blank=True)
    colors = ArrayField(base_field=models.CharField(max_length=20), verbose_name=_('Available Colors'), null=True,
                        blank=True)
    dimensions = models.CharField(max_length=30, verbose_name=_('Dimensions'), null=True, blank=True)
    reference = models.CharField(max_length=30, verbose_name=_('Reference'), null=True, blank=True)
    stock = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    category = models.ForeignKey('SubCategory', on_delete=do_nothing, related_name='products',
                                 verbose_name=_('Category'), null=True)
    free_delivery = models.BooleanField(default=False, verbose_name=_('Free Delivery'))

    def __str__(self):
        return self.name

    @property
    def overall(self):
        return (self.ratings
                .filter(visible=True)
                .aggregate(overall=Avg('stars')).get('overall', 0.0) or decimal.Decimal(0.0)) \
                   .quantize(decimal.Decimal("0.0")) or 0.0

    @property
    def total_reviews_count(self):
        return self.ratings.filter(visible=True).count()

    @property
    def reviews_count_based_on_stars(self):
        return [self.ratings.filter(visible=True, stars__lte=1).count(),
                self.ratings.filter(visible=True, stars__in=[1, 2.1]).count(),
                self.ratings.filter(visible=True, stars__in=[2.1, 3.1]).count(),
                self.ratings.filter(visible=True, stars__in=[3.1, 4]).count(),
                self.ratings.filter(visible=True, stars__in=[4.1, 5.1]).count()]

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')


class OrderLine(BaseModel):
    product = models.ForeignKey('Product', related_name='orders_lines', on_delete=do_nothing)
    order = models.ForeignKey('Order', related_name='lines', on_delete=do_nothing)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Quantity'))
    on_discount = models.BooleanField(default=False, verbose_name=_('On Discount'))

    def __str__(self):
        return '{} {}'.format(self.quantity, self.product)

    @property
    def total(self):
        return (self.product.price * self.quantity).quantize(decimal.Decimal("0.01"))

    class Meta:
        verbose_name = _('Order Line')
        verbose_name_plural = _('Order Lines')

    def delete(self, using=None, keep_parents=False):
        data = super(OrderLine, self).delete(using, keep_parents)
        from ecommerce.signals import order_line_deleted
        order_line_deleted.send(sender=self.__class__, instance=self)
        return data


class Order(DeletableModel):
    # add return status
    status_choices = (('P', _('Pending')),
                      ('RC', _('RECALL')),
                      ('CO', _('Confirmed')),
                      ('CA', _('Canceled')),
                      ('OD', _('On Delivery')),
                      ('D', _('Delivered')),
                      ('R', _('Returned')),
                      ('RE', _('Refund')),
                      ('PA', _('Paid')),
                      ('NA', _('No Answer')),)

    profile = models.ForeignKey('accounts.Profile', related_name='orders', on_delete=do_nothing)
    number = models.CharField(max_length=16, unique=True, verbose_name=_('Order Number'))
    status = models.CharField(max_length=2, choices=status_choices, verbose_name=_('Order Status'), default='P')
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Shipping Fee'), default=0)
    free_delivery = models.BooleanField(default=False, blank=True)
    assigned_to = models.ForeignKey("accounts.User", on_delete=do_nothing, null=True, blank=True,
                                    verbose_name=_("Assigned To"), related_name="orders")

    @property
    def products_count(self):
        return self.get_lines.aggregate(count=Sum('quantity')).get('count', 0)

    @property
    def sub_total(self):
        total = decimal.Decimal(0.0)
        for line in self.get_lines:
            total += line.total
        return total.quantize(decimal.Decimal("0.01"))

    @property
    def total_sum(self):
        sub_total = self.sub_total
        total = sub_total + self.shipping_fee
        return total.quantize(decimal.Decimal("0.01"))

    @property
    def client_total_display(self):
        return self.total_sum if not self.free_delivery else self.sub_total

    @property
    def get_lines(self):
        return self.lines.filter()

    @staticmethod
    def generate_number():
        from random import randint
        return randint(11111, 99999)

    def __str__(self):
        return '{}'.format(self.number)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def progress_status(self):
        if self.status == 'P':
            self.status = 'CO'
        elif self.status == 'CO':
            self.status = 'OD'
        elif self.status == 'OD':
            self.status = 'D'
        else:
            self.status = 'CO'
        self.save()

    def delete(self, using=None, keep_parents=False):
        if self.status == 'D':
            return
        self.status = 'CA'
        super(Order, self).delete(using=using, keep_parents=keep_parents)

    @property
    def get_delivery_guy(self) -> str:
        try:
            return self.deliveries.all().first().delivery_guys.name
        except AttributeError:
            return ""

    def render_as_printable(self) -> list:
        columns = (_('Product'), _('Price'), _('Quantity'), _('Total'))
        data = [columns]
        for line in self.get_lines:
            line_data = [line.product.name, line.product.price, line.quantity, line.total]
            data.append(line_data)
        bottom_row = [" ", " ", " ", self.total_sum]
        data.append(bottom_row)

        return data


class OrderStatusChange(BaseModel):
    order = models.ForeignKey('Order', on_delete=do_nothing, related_name='status_changes', verbose_name=_('Order'))
    previous_status = models.CharField(max_length=2, choices=Order.status_choices, verbose_name=_('Previous Status'))
    new_status = models.CharField(max_length=2, choices=Order.status_choices, verbose_name=_('New Status'))
    user = models.ForeignKey('accounts.User', on_delete=do_nothing, related_name='status_changes', )


class Favorite(DeletableModel):
    profile = models.ForeignKey('accounts.Profile', related_name='favorites', on_delete=do_nothing)
    product = models.ForeignKey('Product', related_name='favorites', on_delete=do_nothing)

    class Meta:
        verbose_name = _('Favorite')
        verbose_name_plural = _('Favorites')


class Rate(DeletableModel):
    stars = models.DecimalField(max_digits=2, decimal_places=1, verbose_name=_('Stars'))
    comment = models.CharField(max_length=255, null=True, verbose_name=_('Comment'))
    profile = models.ForeignKey('accounts.Profile', related_name='ratings', on_delete=do_nothing)
    product = models.ForeignKey('Product', related_name='ratings', on_delete=do_nothing)

    class Meta:
        verbose_name = _('Rating')
        verbose_name_plural = _('Ratings')

    @property
    def checked_stars_range(self):
        return range(0, int(self.stars))

    @property
    def un_checked_stars_range(self):
        return range(0, 5 - int(self.stars))

    def __str__(self):
        return f'{self.comment}'


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

    def _total_sum(self):
        return self.product.price * self.quantity

    @property
    def total_sum(self):
        return self._total_sum().quantize(decimal.Decimal("0.01"))

    @property
    def total(self):
        return self.total_sum

    def to_order_line(self, order):
        return OrderLine.objects.create(product=self.product, quantity=self.quantity, order=order)

    class Meta:
        verbose_name = _('Cart Line')
        verbose_name_plural = _('Cart Lines')


class Cart(DeletableModel):
    profile = models.OneToOneField('accounts.Profile', related_name='cart', on_delete=do_nothing)

    @property
    def total_sum(self):
        return self.lines.aggregate(total=Sum(F('quantity') * F('product__price'))).get('total', 0.0) \
            .quantize(decimal.Decimal('0.01'))

    @property
    def products_count(self):
        return self.get_lines.aggregate(count=Sum('quantity')).get('count', 0)

    @property
    def get_lines(self):
        return self.lines.filter(visible=True)

    def confirm(self):
        order = Order.objects.create(profile=self.profile)
        for line in self.get_lines:
            line.to_order_line(order=order)
        self.clear_lines()
        return order

    def clear_lines(self):
        self.lines.update(visible=False)

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


class DeliveryCompany(DeletableModel):
    company_name = models.CharField(unique=True, verbose_name=_('Company Name'), max_length=255)
    weight_threshold = models.PositiveIntegerField(verbose_name=_('Weight Threshold'), default=0, blank=True)
    base_fee = models.PositiveIntegerField(verbose_name=_('Base Fee'), default=0, blank=True)

    @property
    def delivery_guys_count(self) -> int:
        return self.delivery_guys.count()

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = _('Delivery Company')
        verbose_name_plural = _('Delivery Companies')


class DeliveryGuy(DeletableModel):
    name = models.CharField(unique=True, max_length=50, verbose_name=_('Name'))
    company = models.ForeignKey('DeliveryCompany', on_delete=cascade, null=True, blank=True,
                                related_name="delivery_guys")

    def __str__(self):
        return "{} {}".format(self.name, self.company)

    class Meta:
        verbose_name = _('Delivery Guy')
        verbose_name_plural = _('Delivery Guys')


class Deliveries(DeletableModel):
    order = models.ForeignKey('Order', on_delete=cascade, verbose_name=_('Order'), related_name="deliveries")
    delivery_guys = models.ForeignKey('DeliveryGuy', on_delete=cascade, verbose_name=_('Delivery Guy'),
                                      related_name="deliveries")
    delivery_date = models.DateField(_("Delivery Date"), null=True, blank=True)

    @property
    def fee(self) -> int:
        return 0

    def __str__(self) -> str:
        return f'{self.delivery_guys.name} is delivering {self.order.number}'

    class Meta:
        verbose_name = _('Delivery')
        verbose_name_plural = _('Deliveries')


class DeliveryFee(DeletableModel):
    state = models.ForeignKey('accounts.State', related_name='fees', on_delete=do_nothing)
    company = models.ForeignKey('DeliveryCompany', on_delete=do_nothing, related_name='fees')
    fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('Delivery Fee')
        verbose_name_plural = _('Delivery Fees')


class IndexContent(BaseModel):
    # card 1 attrs
    card1_visibility = models.BooleanField(default=True, verbose_name=_("Visibility"))
    card1_header = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("Header"))
    card1_title = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Title"))
    card1_content = models.TextField(null=True, blank=True, verbose_name=_("Content Text"))
    card1_button_text = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Button Text"))
    card1_image = models.ImageField(verbose_name=_("Image"), null=True, blank=True, upload_to='index')

    # section 1 attrs
    section1_title = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("Title"))
    section1_text = models.TextField(null=True, blank=True, verbose_name=_("Content Text"))
    section1_categories = models.ManyToManyField("Category", related_name="index_cats",
                                                 verbose_name=_("Display Categories"))

    # section 2 attrs
    section2_title = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("Title"))
    section2_text = models.TextField(null=True, blank=True, verbose_name=_("Content Text"))
    section2_button_text = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Button Text"))
    section2_image = models.ImageField(verbose_name=_("Image"), null=True, blank=True, upload_to='index')

    # section 3 attrs
    section3_title = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("Title"))
    section3_text = models.TextField(null=True, blank=True, verbose_name=_("Content Text"))
    section3_button_text = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Button Text"))

    # section 4 attrs
    section4_title = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("Title"))
    section4_text = models.TextField(null=True, blank=True, verbose_name=_("Content Text"))
    section4_button_text = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Button Text"))
    section4_image1 = models.ImageField(null=True, blank=True, verbose_name=_("Image 1"), upload_to='index')
    section4_image2 = models.ImageField(null=True, blank=True, verbose_name=_("Image 2"), upload_to='index')

    # section 5 attrs
    section5_title = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("Title"))
    section5_text = models.TextField(null=True, blank=True, verbose_name=_("Content Text"))
    section5_button_text = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Button Text"))

    assistance_number = models.CharField(max_length=30, verbose_name=_("Assistance Number"), null=True)


class Partner(DeletableModel):
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("Name"))
    url = models.URLField(null=True, blank=True, verbose_name=_("URL"))

    class Meta:
        verbose_name = _('Partner')
        verbose_name_plural = _('Partners')

    def __str__(self):
        return f'{self.name}'


class Complaint(DeletableModel):
    COMPLAINTS = (
        ('DP', _('Delivery Problem')),
        ('PP', _('Product Problem')),
        ('SP', _('Service Problem')),
        ('O', _('Other')),
    )

    client = models.ForeignKey('accounts.User', related_name="complaints", verbose_name=_('Client'),
                               on_delete=do_nothing)
    complaint = models.CharField(choices=COMPLAINTS, max_length=2, verbose_name=_("Complaint"))
    against = models.ForeignKey('DeliveryGuy', related_name="complaints", verbose_name=_('Against'),
                                on_delete=do_nothing, null=True, blank=True)
    comment = models.TextField(verbose_name=_('Comment'), max_length=500, null=True, blank=True)
    treated = models.BooleanField(default=False, verbose_name=_('Treated'), blank=True)
    order = models.ForeignKey('Order', related_name=_('complaints'), verbose_name=_('Order'), on_delete=do_nothing,
                              null=True, blank=True)
