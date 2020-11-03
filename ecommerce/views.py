import json

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, F, Count
from django.forms import formset_factory
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView, FormView, TemplateView, \
    RedirectView

# Create your views here.
from accounts.models import User, State
from base_backend.utils import get_current_week, is_ajax
from ecommerce.forms import CreateOrderLineForm, CreateProductForm
from ecommerce.models import Product, Order, OrderLine, Favorite, Cart, CartLine, Category, SubCategory
from base_backend import _


class Index(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        m_kwargs = super(Index, self).get_context_data(**kwargs)
        m_kwargs['popular_cats'] = Category.objects.category_with_3_products()[:3]
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
    extra_context = {'categories_json': json.dumps(Category.objects.with_sub_cats()),
                     'categories': Category.objects.filter(visible=True)}
    page_kwarg = 'page'
    paginate_by = 25
    allow_empty = True
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super(DashboardProductsListView, self).get_queryset()
        for item in queryset:
            print(item.main_image.url)
        if self.request.GET.get('category', None):
            queryset = queryset.filter(
                category__category_id=self.request.GET.get('category', None))
        if self.request.GET.get('sub_category', None):
            queryset = queryset.filter(
                category_id=self.request.GET.get('sub_category', None))
        return queryset

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            super(DashboardProductsListView, self).get(request, *args, **kwargs)
            context = self.get_context_data()
            data = dict()
            data['products'] = render_to_string('dashboard/_products_table.html',
                                                {'products': context.pop('products', None)},
                                                request=request)
            return JsonResponse(data)
        else:
            return super(DashboardProductsListView, self).get(request, *args, **kwargs)


class ViewProductDetailsView(DetailView):
    model = Product
    context_object_name = 'product'
    queryset = Product.objects.filter(visible=True)
    template_name = "product_details.html"

    def get_context_data(self, **kwargs):
        m_context = super(ViewProductDetailsView, self).get_context_data(**kwargs)
        product = kwargs.get('product', kwargs.get('object', None))
        if product and self.request.user.is_authenticated:
            m_context['is_favorite'] = product.id in self.request.user.profile.favorites.all().values_list('product',
                                                                                                           flat=True)
        return m_context


class ProductsListView(ListView):
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(visible=True)
    template_name = "products.html"
    paginate_by = 21
    page_kwarg = 'page'
    paginate_orphans = True
    ordering = ['-created_at']


@method_decorator(staff_member_required, name='dispatch')
class CreateProduct(BSModalCreateView):
    model = Product
    context_object_name = 'product'
    success_url = reverse_lazy("ecommerce:dashboard-products")
    template_name = "dashboard/create_product.html"
    success_message = _("Product Created Successfully")
    form_class = CreateProductForm

    def form_invalid(self, form):
        print(form.errors)
        return super(CreateProduct, self).form_invalid(form=form)

    def form_valid(self, form):
        print("success")
        print(form.cleaned_data)
        form.save()
        return super(CreateProduct, self).form_valid(form=form)


@method_decorator(staff_member_required, name='dispatch')
class UpdateProduct(BSModalUpdateView):
    model = Product
    context_object_name = 'product'
    form_class = CreateProductForm
    success_url = reverse_lazy("ecommerce:dashboard-products")
    template_name = "dashboard/create_product.html"
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
class RedirectToCartDetailsView(RedirectView):
    permanent = True
    pattern_name = 'ecommerce:cart-details'

    def get_redirect_url(self, *args, **kwargs):
        url = reverse(self.pattern_name, kwargs={'pk': self.request.user.profile.cart.id})
        return url


@method_decorator(login_required, name='dispatch')
class CartDetailsView(DetailView, CartMixin):
    model = Cart
    template_name = "cart.html"
    context_object_name = "cart"
    queryset = Cart.objects.filter(visible=True)

    def get_queryset(self):
        queryset = super(CartDetailsView, self).get_queryset()
        return self.my_get_queryset(queryset)


@method_decorator(login_required, name='dispatch')
class CartAddView(CreateView):
    model = CartLine
    context_object_name = "cart_line"
    fields = ['product', 'cart', 'quantity']
    template_name = "index.html"
    success_url = reverse_lazy('ecommerce:index')

    def get_initial(self):
        initials = super(CartAddView, self).get_initial()
        initials['cart'] = self.request.user.profile.cart
        return initials

    def form_invalid(self, form):
        print(form.errors)
        return super(CartAddView, self).form_invalid(form=form)

    def form_valid(self, form):
        if self.request.is_ajax():
            super(CartAddView, self).form_valid(form=form)
            return JsonResponse({'status': 'Success'})
        else:
            return super(CartAddView, self).form_valid(form=form)


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


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class OrderDeleteView(DeleteView, OrdersMixin):
    model = Order
    template_name = ""
    success_url = ""
    queryset = Order.objects.filter(visible=True)

    def get_queryset(self):
        queryset = super(OrderDeleteView, self).get_queryset()
        return self.my_get_queryset(queryset)


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class OrderLineCreateView(CreateView):
    pass


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class OrderLineDeleteView(DeleteView):
    model = OrderLine
    context_object_name = 'order'
    success_url = ""
    template_name = ""
    queryset = OrderLine.objects.filter(visible=True)

    def get_queryset(self):
        queryset = super(OrderLineDeleteView, self).get_queryset()
        return self.my_get_queryset(queryset)


@method_decorator(login_required, name='dispatch')
class FavoriteCreateView(CreateView):
    model = Favorite
    context_object_name = 'favorite'
    fields = ['product', 'profile']
    template_name = "index.html"
    success_url = reverse_lazy('ecommerce:index')

    def get_initial(self):
        initials = super(FavoriteCreateView, self).get_initial()
        initials['profile'] = self.request.user.profile
        return initials

    def form_invalid(self, form):
        print(form.errors)
        return super(FavoriteCreateView, self).form_invalid(form=form)

    def form_valid(self, form):
        print("success?")
        if self.request.is_ajax():
            super(FavoriteCreateView, self).form_valid(form=form)
            return JsonResponse({'status': 'Success'})
        else:
            return super(FavoriteCreateView, self).form_valid(form=form)


@method_decorator(login_required, name='dispatch')
class FavoriteListView(ListView):
    model = Favorite
    template_name = ""
    context_object_name = "favorites"
    queryset = Favorite.objects.filter(visible=True)

    def get_queryset(self):
        queryset = super(FavoriteListView, self).get_queryset()
        return queryset.filter(profile=self.request.user.profile)


@login_required()
def get_cart_count(request):
    try:
        return JsonResponse({'count': request.user.profile.cart.lines.count()})
    except Exception:
        return JsonResponse({'count': 0})


class CategoriesListView(ListView):
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(visible=True)
    template_name = "categories.html"
    paginate_by = 21
    page_kwarg = 'page'
    paginate_orphans = True
    extra_context = {'categories': Category.objects.filter(visible=True),
                     'sub_categories': SubCategory.objects.filter(visible=True)}
    allow_empty = True
    ordering = 'pk'

    def search(self):
        queries = self.request.GET
        print('start', self.queryset)
        if queries.get('category', None):
            self.queryset = self.queryset.filter(category__category_id=queries.get('category'))
            print('category', self.queryset)
        if queries.get('sub_category', None):
            self.queryset = self.queryset.filter(category_id=queries.get('sub_category'))
            print('sub_category', self.queryset)
        if queries.get('color', 'any') and not queries.get('color', 'any') == 'any':
            self.queryset = self.queryset.filter(colors__contains=[queries.get('color')])
            print('color', self.queryset)
        if queries.get('from', 0):
            self.queryset = self.queryset.filter(price__gte=queries.get('from', 0))
            print('from', self.queryset)
        if queries.get('to', 0):
            self.queryset = self.queryset.filter(price__lte=queries.get('to', 0))
            print('to', self.queryset)
        if queries.get('period'):
            integer = 0
            # todo implement the cases for this

    def get(self, request, *args, **kwargs):
        self.search()
        return super(CategoriesListView, self).get(request, *args, **kwargs)
