from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Count
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView, FormView, TemplateView, \
    RedirectView

# Create your views here.
from accounts.models import User, State
from base_backend.utils import get_current_week
from ecommerce.forms import CreateOrderLineForm, CreateProductForm
from ecommerce.models import Product, Order, OrderLine, Favorite, Cart, CartLine, Category
from base_backend import _


class Index(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        m_kwargs = super(Index, self).get_context_data(**kwargs)
        m_kwargs['popular_cats'] = Category.objects.filter(visible=True)
        m_kwargs['random_products'] = Product.objects.filter(visible=True).order_by('?')[:3]
        m_kwargs['top_pick'] = Product.objects.filter(visible=True).annotate(pick_count=Count('orders_lines')).order_by(
            '-pick_count')[:3]
        return m_kwargs


@method_decorator(staff_member_required, name='dispatch')
class Dashboard(TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        m_kwargs = super(Dashboard, self).get_context_data(**kwargs)
        m_kwargs["total_users"] = User.objects.filter(user_type="C").count()
        m_kwargs["items_sold"] = OrderLine.objects.filter(visible=True).aggregate(count=Sum('quantity')) \
                                     .get('count', 0) or 0
        m_kwargs["items_sold_week"] = OrderLine.objects.filter(visible=True, created_at__week=get_current_week()) \
                                          .aggregate(count=Sum('quantity')).get('count', 0) or 0
        m_kwargs["earnings"] = OrderLine.objects.filter(visible=True) \
            .aggregate(earning=Sum(F('quantity') * F('product__price'))).get('total', 0)
        m_kwargs["states"] = State.objects.all()[:10]
        return m_kwargs


class DashboardProductsListView(ListView):
    template_name = "dashboard/products_list.html"
    queryset = Product.objects.all()
    model = Product
    context_object_name = "products"
    extra_context = {'categories': Category.objects.all()}
    page_kwarg = 'page'
    paginate_by = 25
    allow_empty = False
    ordering = 'created_at'


class ViewProductDetailsView(DetailView):
    model = Product
    context_object_name = 'product'
    queryset = Product.objects.filter(visible=True)
    template_name = ""


class ProductsListView(ListView):
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(visible=True)
    template_name = ""


@method_decorator(staff_member_required, name='dispatch')
class CreateProduct(CreateView):
    model = Product
    context_object_name = 'product'
    success_url = reverse_lazy("ecommerce:dashboard-products")
    template_name = "dashboard/create_product.html"
    success_message = _("Product Created Successfully")
    form_class = CreateProductForm

    def form_invalid(self, form):
        print(form.errors)
        return super(CreateProduct, self).form_invalid(form=form)


@method_decorator(staff_member_required, name='dispatch')
class UpdateProduct(UpdateView):
    model = Product
    context_object_name = 'product'
    fields = ['name', 'name_ar', 'name_en', 'description', 'description_ar', 'description_en', 'price', 'main_image',
              'slider', 'discount_price', 'colors', 'dimensions']
    success_url = ""
    template_name = ""
    queryset = Product.objects.filter(visible=True)


@method_decorator(staff_member_required, name='dispatch')
class DeleteProduct(RedirectView):
    permanent = True
    pattern_name = "ecommerce:dashboard-products"

    def get_redirect_url(self, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs['pk'])
        product.delete()
        return reverse("ecommerce:dashboard-products")


# cart

class CartMixin:
    def my_get_queryset(self, queryset):
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(profile=self.request.user.profile)


@method_decorator(login_required, name='dispatch')
class CartDetailsView(DetailView, CartMixin):
    model = Cart
    template_name = ""
    context_object_name = "cart"
    queryset = Cart.objects.filter(visible=True)

    def get_queryset(self):
        queryset = super(CartDetailsView, self).get_queryset()
        return self.my_get_queryset(queryset)


@method_decorator(login_required, name='dispatch')
class CartAddView(CreateView):
    model = CartLine
    template_name = ""
    context_object_name = "cart_line"
    fields = ['product', 'cart', 'quantity']

    def get_initial(self):
        initials = super(CartAddView, self).get_initial()
        initials['cart'] = self.request.user.profile.cart
        return initials


@method_decorator(login_required, name='dispatch')
class CartUpdateView(UpdateView):
    model = CartLine
    template_name = ""
    context_object_name = "cart_line"
    fields = ['product', 'cart', 'quantity']


@method_decorator(login_required, name='dispatch')
class CartRemoveView(DeleteView):
    model = CartLine
    template_name = ""
    context_object_name = "cart_line"


@method_decorator(login_required, name='dispatch')
class CartCashOutToOrder(View):
    pass


# orders and order lines
class OrdersMixin:
    def my_get_queryset(self, queryset):
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(profile=self.request.user.profile)


class OrdersHistory(ListView, OrdersMixin):
    template_name = ""
    ordering = "-created_at"
    queryset = Order.objects.filter(visible=True)
    context_object_name = "orders"

    def get_queryset(self):
        queryset = super(OrdersHistory, self).get_queryset()
        return self.my_get_queryset(queryset)

    def get_context_data(self, **kwargs):
        context = super(OrdersHistory, self).get_context_data(**kwargs)
        total = 0
        if kwargs.get('object_list'):
            for order in kwargs.get('object_list'):
                total += order.sub_total
        context['total'] = total
        return context


class OrderCreateView(FormView):
    model = Order
    context_object_name = 'order'
    form_class = formset_factory(CreateOrderLineForm, extra=1, min_num=1, validate_min=True)
    success_url = ""
    template_name = ""

    def get_initial(self):
        initials = super(OrderCreateView, self).get_initial()
        initials['profile'] = self.request.user.profile
        return initials

    def form_valid(self, forms):
        order = Order.objects.create(number=Order.generate_number(), profile=self.request.user.profile)

        def assign_order_to_line(line_form):
            line_form.order = order
            line_form.save()

        map(assign_order_to_line, forms)
        return HttpResponseRedirect(self.get_success_url(), pk=order.pk)


class OrderUpdateView(UpdateView, OrdersMixin):
    model = Order
    context_object_name = 'order'
    fields = ['profile', 'number', 'status']
    success_url = ""
    template_name = ""
    queryset = Order.objects.filter(visible=True)

    def get_queryset(self):
        queryset = super(OrderUpdateView, self).get_queryset()
        return self.my_get_queryset(queryset)


class OrderDeleteView(DeleteView, OrdersMixin):
    model = Order
    template_name = ""
    success_url = ""
    queryset = Order.objects.filter(visible=True)

    def get_queryset(self):
        queryset = super(OrderDeleteView, self).get_queryset()
        return self.my_get_queryset(queryset)


class OrderDetails(DetailView, OrdersMixin):
    model = Order
    context_object_name = 'order'
    queryset = Order.objects.filter(visible=True)
    template_name = ""

    def get_queryset(self):
        queryset = super(OrderDetails, self).get_queryset()
        return self.my_get_queryset(queryset)


class OrderLineMixin:
    def my_get_queryset(self, queryset):
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(order__profile=self.request.user.profile)


class OrderLineCreateView(CreateView):
    pass


class OrderLineUpdateView(UpdateView):
    model = OrderLine
    context_object_name = 'order'
    fields = ['product', 'quantity']
    success_url = ""
    template_name = ""
    queryset = OrderLine.objects.filter(visible=True)

    def get_queryset(self):
        queryset = super(OrderLineUpdateView, self).get_queryset()
        return self.my_get_queryset(queryset)


class OrderLineDeleteView(DeleteView):
    model = OrderLine
    context_object_name = 'order'
    success_url = ""
    template_name = ""
    queryset = OrderLine.objects.filter(visible=True)

    def get_queryset(self):
        queryset = super(OrderLineDeleteView, self).get_queryset()
        return self.my_get_queryset(queryset)


class FavoriteCreateView(CreateView):
    model = Favorite
    context_object_name = 'favorite'

    def get_initial(self):
        initials = super(FavoriteCreateView, self).get_initial()
        initials['profile'] = self.request.user.profile
        return initials


class FavoriteListView(ListView):
    model = Favorite
    template_name = ""
    context_object_name = "favorites"
    queryset = Favorite.objects.filter(visible=True)

    def get_queryset(self):
        queryset = super(FavoriteListView, self).get_queryset()
        return queryset.filter(profile=self.request.user.profile)
